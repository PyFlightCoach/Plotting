from collections.abc import Callable
from typing import Literal

import geometry as g
import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flightdata import State
from plotly.subplots import make_subplots

from plotting.model import OBJ, obj
from plotting.traces import (
    aoa_trace,
    axestrace,
    axis_rate_trace,
    cgtrace,
    control_input_trace,
    meshes,
    ribbon,
    tiptrace,
    vectors,
)


def get_colour(i):
    return px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]


def plotsec(
    secs: State | list[State] | dict[str, State],
    scale=5,
    nmodels=0,
    fig=None,
    color: str | list[str] | None = None,
    cg=False,
    width=None,
    height=None,
    show_axes=False,
    ribb: bool = False,
    tips: bool = True,
    ribbonhover="t",
    origin=False,
    line=None,
    modelscale=1,
    model: OBJ = None,
    row: int | None = None,
    col: int | None = None,
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

    def _get_colour(i):
        if isinstance(color, list):
            return color[i % len(color)]
        elif isinstance(color, str):
            return color
        else:
            return get_colour(i)

    for i, sec in enumerate(secs):
        text = sec.t  # - sec.data.t.iloc[0]

        if ribb:
            traces += ribbon(
                sec,
                0.5 * scale * 1.85,
                _get_colour(i),
                name=keys[i],
                opacity=0.5,
                hover=ribbonhover,
            )
        if tips:
            traces += tiptrace(
                sec,
                scale * 1.85,
                text=text,
                name=keys[i],
                line=({} if line is None else line),
            )
        if nmodels > 0:
            traces += meshes(
                nmodels, sec, _get_colour(i), scale * modelscale, _obj=model
            )
        if cg:
            traces.append(
                cgtrace(
                    sec,
                    line={"color": _get_colour(i), "width": 2}
                    | ({} if line is None else line),
                    name=keys[i],
                    text=text,
                )
            )

    if origin:
        traces += axestrace(g.Coord.zero(), 50)

    if showkeys:
        for i, key in enumerate(keys):
            traces.append(
                go.Scatter3d(
                    x=[],
                    y=[],
                    z=[],
                    mode="markers",
                    marker={"size": 5, "color": _get_colour(i)},
                    name=key,
                    showlegend=True,
                )
            )

    if fig is None:
        fig = go.Figure(
            data=traces,
            layout=go.Layout(template="flight3d", uirevision="foo"),
        )
        if show_axes:
            fig.update_layout(
                scene={
                    "aspectmode": "data",
                    "xaxis": {"visible": True, "showticklabels": True},
                    "yaxis": {"visible": True, "showticklabels": True},
                    "zaxis": {"visible": True, "showticklabels": True},
                }
            )
        if width is not None:
            fig.update_layout(width=width)
        if height is not None:
            fig.update_layout(height=height)
    else:
        fig.add_traces(traces, rows=row, cols=col)
    return fig


def plotdtw(sec: State, manoeuvres: list[str], span=3, fig=None):
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
                    line={"width": 6, "color": px.colors.qualitative.Alphabet[i]},
                    name=name,
                )
            )
        except Exception as ex:
            print(f"no data for manoeuvre {name}, {ex}")

    fig.add_traces(traces)

    return fig


def plot_regions(
    st: State,
    label_group_name: str,
    span=3,
    colours=None,
    fig=None,
    ribbonhover="t",
    rename: dict[str, str] | None = None,
    **kwargs,
):
    colours = px.colors.qualitative.Plotly if colours is None else colours

    traces = []
    for i, k in enumerate(st.labels[label_group_name].keys()):
        seg = getattr(st, label_group_name)[k]
        if len(seg) < 3:
            continue
        traces += ribbon(
            seg,
            span,
            colours[i % len(colours)],
            name=k if rename is None else rename.get(k, k),
            hover=ribbonhover,
        )

    if fig is None:
        fig = go.Figure(layout=go.Layout(template="flight3d+judge_view"))
    fig.add_traces(traces)
    return fig


def create_3d_plot(traces):
    return go.Figure(traces, layout=go.Layout(template="flight3d+judge_view"))


nb_layout = {
    "margin": {"l": 5, "r": 5, "t": 5, "b": 1},
    "legend": {"yanchor": "top", "xanchor": "left", "x": 0.8, "y": 0.99},
}


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

    sceneids = [f"scene{i + 1}" for i in range(ncols * nrows)]
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
        scene={
            "aspectmode": "data",
            "xaxis": {"visible": True, "showticklabels": True},
            "yaxis": {"visible": True, "showticklabels": True},
            "zaxis": {"visible": True, "showticklabels": True},
        },
        height=800,
    )
    return fig


def multi_y_subplots(data: dict[str, pd.DataFrame], x: npt.NDArray = None):
    fig = make_subplots(
        rows=len(data),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01,
        # subplot_titles=list(data.keys()),
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
                    title=list(data.keys())[i - 1],
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


def create_ortho_state(
    st: State, axis: Literal["x", "z"], width: g.Point, gap: g.Point
) -> State:
    """rotate by 90 degrees about the given axis,
    then move to where it should be in an orthographic projection.
    assumes front view is along the Y axis (x right, z up).
    also assumes state is centered at the origin.
    """
    st = st.move(
        g.Transformation(
            g.Euler(np.pi / 2 if axis == "x" else 0, 0, np.pi / 2 if axis == "z" else 0)
        )
    )

    if axis == "x":
        shift = g.PZ((width.y + width.z) / 2 + gap)
    elif axis == "z":
        shift = g.PX(-(width.x + width.y) / 2 - gap)

    st = st.move(g.Transformation(shift))  # move back to center and offset by shift

    return st


def applysts(
    st: State | list[State] | dict[str, State], fun: Callable[[State], State]
) -> State | list[State] | dict[str, State]:
    """apply a transformation to all states in a list or dict of states"""
    if isinstance(st, State):
        return fun(st)
    elif isinstance(st, list):
        return [fun(s) for s in st]
    elif isinstance(st, dict):
        return {k: fun(v) for k, v in st.items()}


def get_points(fig: go.Figure) -> g.Point:
    """extract all points from a figure"""
    ps = []
    for d in fig.data:
        try:
            ps.append(g.Point(d.x, d.y, d.z))
        except Exception:
            pass
    return g.Point.concatenate(ps)


def plot_3view(
    st: State | list[State] | dict[str, State],
    plotfun: Callable,
    gap: float,
    legend_vstep=10,
):

    allsts = State.stack(st, "grp") if not isinstance(st, State) else st

    width = allsts.pos.max() - allsts.pos.min()
    center = allsts.pos.min() + width / 2

    st0 = applysts(st, lambda s: s.move(g.Transformation(-center)))
    st1 = applysts(st0, lambda s: create_ortho_state(s, "x", width, gap))
    st2 = applysts(st0, lambda s: create_ortho_state(s, "z", width, gap))

    fig = go.Figure(data=plotfun(st0) + plotfun(st1) + plotfun(st2))

    anprops = dict(
        showarrow=False,
        font=dict(size=16, family="Rockwell"),
        xanchor="center",
        yanchor="middle",
    )

    fig = fig.update_layout(
        template="plotly_white",
        scene=dict(
            camera=dict(
                eye=dict(x=0, y=-1, z=0),
                center=dict(x=0, y=0, z=0),
                projection=dict(type="orthographic"),
            ),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            annotations=[
                dict(
                    x=0,
                    y=0,
                    z=-width.z[0] / 2 - gap / 2,
                    text="Front View",
                )
                | anprops,
                dict(
                    x=0,
                    y=0,
                    z=width.z[0] / 2 + width.y[0] / 2 + gap / 2,
                    text="Top View",
                )
                | anprops,
                dict(
                    x=-width.x[0] / 2 - width.y[0] / 2 - gap,
                    y=0,
                    z=-width.z[0] / 2 - gap / 2,
                    text="Left View",
                )
                | anprops,
            ]
            + (
                []
                if not isinstance(st, dict)
                else [
                    dict(
                        x=-width.x[0] / 2 - width.y[0] / 2 - gap,
                        y=0,
                        z=width.z[0] / 2 + width.y[0] / 2 + gap / 2 + i * legend_vstep,
                        text=k,
                        font=dict(
                            size=16,
                            family="Rockwell",
                            color=px.colors.qualitative.Plotly[i],
                        ),
                        showarrow=False,
                    )
                    for i, k in enumerate(st.keys())
                ]
            ),
        ),
        margin=dict(l=0, r=0, b=0, t=0),
    )

    return resize_3d_fig(fig, 600, False)


def resize_3d_fig(
    fig: go.Figure, width: int | None, width_is_height: bool = False, scale: float = 1
):
    """Resize a figure to the given width, height and zoom level.
    preserves the aspect ratio of the scene.
    Assumes view is in the positive Y direction
    """

    all_points = get_points(fig)

    btm_left = all_points.min()
    top_right = all_points.max()

    bb = top_right - btm_left
    width = width or (fig.layout.height if width_is_height else fig.layout.width) or 600
    zoom = 0.008 * scale * width / (bb.z[0] if width_is_height else bb.x[0])
    ar = bb * zoom
    height = ar.x[0] * width / ar.z[0] if width_is_height else ar.z[0] * width / ar.x[0]
    fig.update_layout(
        width=height if width_is_height else width,
        height=width if width_is_height else height,
        scene=dict(
            aspectratio=dict(x=ar.x[0], y=ar.y[0], z=ar.z[0]),
            camera=dict(
                eye=dict(x=0, y=-1, z=0),
                center=dict(x=0, y=0, z=0),
                projection=dict(type="orthographic"),
            ),
        ),
    )

    return fig
