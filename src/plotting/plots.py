import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotting.templates
from plotting.traces import (
    tiptrace,
    meshes,
    control_input_trace,
    axis_rate_trace,
    aoa_trace,
    cgtrace,
    ribbon,
    vectors,
    axestrace,
)

from flightdata import State
from flightdata.base.labeling import get_appended_id
from geometry import Coord
from plotting.model import obj
import numpy.typing as npt
import numpy as np
import pandas as pd
from typing import List, Union
from flightanalysis.scoring.box import Box


def plotsec(
    secs: State | list[State] | dict[str, State],
    scale=5,
    nmodels=0,
    fig=None,
    color: Union[str, list[str]] = None,
    cg=False,
    width=None,
    height=None,
    show_axes=False,
    ribb: bool = False,
    tips: bool = True,
    origin=False,
):
    traces = []
    keys = None
    if isinstance(secs, State):
        secs = [secs]

    if isinstance(secs, dict):
        keys = list(secs.keys())
        secs = list(secs.values())
        showkeys = True
    else:
        keys = list(range(len(secs)))
        showkeys = False

    for i, sec in enumerate(secs):
        text = sec.data.t #- sec.data.t.iloc[0]
        _color = color if color is not None else px.colors.qualitative.Plotly[i]
        if ribb:
            traces += ribbon(sec, scale * 1.85, _color, name=keys[i])
        if tips:
            traces += tiptrace(sec, scale * 1.85, text=text, name=keys[i])
        if nmodels > 0:
            traces += meshes(nmodels, sec, _color, scale)
        if cg:
            traces.append(cgtrace(sec, line=dict(color=_color, width=2), name=keys[i], text=text))

    if origin:
        traces += axestrace(Coord.zero(), 50)

    if showkeys:
        for i, key in enumerate(keys):
            traces.append(
                go.Scatter3d(
                    x=[],
                    y=[],
                    z=[],
                    mode="markers",
                    marker=dict(size=5, color=px.colors.qualitative.Plotly[i]),
                    name=key,
                    showlegend=True,
                )
            )

    if fig is None:
        fig = go.Figure(
            data=traces,
            layout=go.Layout(template="flight3d+judge_view", uirevision="foo"),
        )
        if show_axes:
            fig.update_layout(
                scene=dict(
                    aspectmode="data",
                    xaxis=dict(visible=True, showticklabels=True),
                    yaxis=dict(visible=True, showticklabels=True),
                    zaxis=dict(visible=True, showticklabels=True),
                )
            )
        if width is not None:
            fig.update_layout(width=width)
        if height is not None:
            fig.update_layout(height=height)
    else:
        fig.add_traces(traces)
    return fig


def plotdtw(sec: State, manoeuvres: List[str], span=3, fig=None):
    if fig is None:
        fig = go.Figure(layout=go.Layout(template="flight3d+judge_view"))

    traces = []  # tiptrace(sec, span)

    for i, name in enumerate(manoeuvres):
        try:
            seg = sec.get_man_or_el(name)

            traces += ribbon(seg, span, px.colors.qualitative.Alphabet[i], name)

            traces.append(
                go.Scatter3d(
                    x=seg.pos.x,
                    y=seg.pos.y,
                    z=seg.pos.z,
                    mode="lines",
                    line=dict(width=6, color=px.colors.qualitative.Alphabet[i]),
                    name=name,
                )
            )
        except Exception as ex:
            pass
            print("no data for manoeuvre {}, {}".format(name, ex))

    fig.add_traces(traces)

    return fig


def plot_regions(
    st: State, lab_cols: list[str], span=3, colours=None, fig=None, box:Box=None, **kwargs
):
    colours = px.colors.qualitative.Plotly if colours is None else colours
    lab_cols = [lab_cols] if isinstance(lab_cols, str) else lab_cols

    st = st.label(clabs=st.cumulative_labels(*lab_cols))

    colmap = {}

    traces = []
    for i, (k, seg) in enumerate(st.split_labels("clabs").items()):
        if len(seg) < 3:
            continue
        blab, id = get_appended_id(k)
        if blab not in colmap:
            colmap[blab] = colours[len(colmap) % len(colours)]
        traces += ribbon(
            seg,
            span,
            colmap[blab],
            name=blab,
            showlegend=int(id) == 0,
            **kwargs[blab] if blab in kwargs else {},
        )
        traces.append(
            go.Scatter3d(
                x=seg.pos.x,
                y=seg.pos.y,
                z=seg.pos.z,
                mode="lines",
                line=dict(width=0, color=colmap[blab]),
                name=k,
                showlegend=False,
            )
        )

    if fig is None:
        fig = go.Figure(layout=go.Layout(template="flight3d+judge_view"))
    fig.add_traces(traces)
    if box:
        fig.add_traces(box.plot())
    return fig


def create_3d_plot(traces):
    return go.Figure(traces, layout=go.Layout(template="flight3d+judge_view"))


nb_layout = dict(
    margin=dict(l=5, r=5, t=5, b=1),
    legend=dict(yanchor="top", xanchor="left", x=0.8, y=0.99),
)


def control_brv_plot(sec, control_inputs=["aileron", "elevator", "rudder", "throttle"]):
    """create a nice 2d plot showing control inputs and rotational velocities for a section"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_traces(axis_rate_trace(sec, dash="dash"), secondary_ys=np.full(3, False))

    fig.add_traces(control_input_trace(sec), secondary_ys=[True for i in range(4)])

    rvrng = np.ceil(np.degrees(sec.brvel.abs().max().max()) / 180) * 180
    cirng = np.ceil(sec.data.loc[:, control_inputs].abs().max().max() / 50) * 50

    fig.update_layout(
        xaxis=dict(title="time, s"),
        yaxis=dict(title="axis rate deg/s", range=(-rvrng, rvrng)),
        yaxis2=dict(title="control pwm offset, ms", range=(-cirng, cirng)),
        **nb_layout,
    )
    return fig


def aoa_brv_plot(sec):
    """create a nice 2d plot showing rotational velocities and angle of attack for a section"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_traces(axis_rate_trace(sec), secondary_ys=np.full(3, False))
    fig.add_traces(
        aoa_trace(sec, colours=px.colors.qualitative.Plotly[4:]),
        secondary_ys=np.full(2, True),
    )
    fig.update_layout(
        xaxis=dict(title="Time (s)"),
        yaxis=dict(title="Axis Rate (deg/s)"),
        yaxis2=dict(title="Angle of Attack (deg)"),
        **nb_layout,
    )
    return fig


def compare_3d(sec1, sec2):
    fig = make_subplots(1, 2, specs=[[{"type": "scene"}, {"type": "scene"}]])
    flowntr = plotsec(sec1, scale=2, nmodels=4).data
    templtr = plotsec(sec2, scale=2, nmodels=4).data

    fig.add_traces(
        flowntr,
        cols=[1 for i in range(len(flowntr))],
        rows=[1 for i in range(len(flowntr))],
    )
    fig.add_traces(
        templtr,
        cols=[2 for i in range(len(templtr))],
        rows=[1 for i in range(len(templtr))],
    )
    fig.update_layout(template="flight3d", showlegend=False)
    return fig


def grid3dplot(plots):
    """takes an n*m list of lists of 3d figures, puts them into a n*m subplot grid"""

    nrows = len(plots)
    ncols = len(plots[0])

    fig = make_subplots(
        cols=len(plots[0]),
        rows=len(plots),
        specs=[[{"type": "scene"} for i in range(ncols)] for j in range(nrows)],
    )

    sceneids = ["scene{}".format(i + 1) for i in range(ncols * nrows)]
    sceneids[0] = "scene"
    fig.update_layout(
        **{
            "scene{}".format(i + 1 if i > 0 else ""): dict(aspectmode="data")
            for i in range(ncols * nrows)
        }
    )

    for ir, plotrow in enumerate(plots):
        for ic, plot in enumerate(plotrow):
            fig.add_traces(
                plot.data,
                cols=np.full(len(plot.data), ic + 1).tolist(),
                rows=np.full(len(plot.data), ir + 1).tolist(),
            )

    return fig


def plot_analysis(
    analysis, obj=obj, nmodels=20, scale=4, cg=False, tip=True, fig=None, **kwargs
):
    obj = obj.scale(scale)

    fig = go.Figure() if not fig else fig

    if cg:
        fig.add_traces(cgtrace(analysis.body, **kwargs))
    if tip:
        fig.add_traces(tiptrace(analysis.body, scale * 1.85))

    fig.add_traces(
        vectors(nmodels, analysis.body, analysis.environment.wind * scale / 3)
    )

    fig.add_traces(meshes(nmodels, analysis.judge, "blue", obj))
    fig.add_traces(meshes(nmodels, analysis.wind, "red", obj))
    fig.add_traces(meshes(nmodels, analysis.body, "green", obj))

    fig.update_layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(visible=True, showticklabels=True),
            yaxis=dict(visible=True, showticklabels=True),
            zaxis=dict(visible=True, showticklabels=True),
        ),
        height=800,
    )
    return fig


def multi_y_subplots(data: dict[str, pd.DataFrame], x: npt.NDArray = None):
    fig = make_subplots(
        rows=len(data),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01,
        #subplot_titles=list(data.keys()),
    )

    for row, (k, v) in enumerate(data.items(), 1):
        for tr, col in enumerate(v.columns):
            fig.add_trace(
                go.Scatter(
                    x=v.index if x is None else np.abs(x),
                    y=v[col],
                    name=f"{k}_{col}",
                    line=dict(
                        color=px.colors.qualitative.Plotly[tr],
                        dash=[
                            "solid",
                            "dot",
                            "dash",
                            "longdash",
                            "dashdot",
                            "longdashdot",
                        ][row % 5],
                    ),
                    legend=f"legend{row}",
                ),
                row=row,
                col=1,
            )

    for i, yaxis in enumerate(fig.select_yaxes(), 1):
        fig.update_layout(
            {
                f"legend{i}": dict(
                    # name = list(data.keys())[i],
                    y=yaxis.domain[1],
                    yanchor="top",
                ),
                f"yaxis{i}": dict(
                    title=list(data.keys())[i-1],
                    showline=True,
                ),
            }
        )

    return fig.update_layout(
        hovermode="x unified",
        hoversubplots="axis",
    )


axis = dict(
    gridcolor="lightgrey",
    linewidth=2,
    linecolor="lightgrey",
    zerolinewidth=2,
    zerolinecolor="lightgrey",
    showline=True,
)
