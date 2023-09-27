import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import flightplotting.templates
from flightplotting.traces import (
    tiptrace, 
    meshes, 
    control_input_trace, 
    axis_rate_trace, 
    aoa_trace, 
    dtwtrace,
    control_inputs,
    cgtrace,
    ribbon,
    vectors,
    axestrace
)
    
from flightanalysis import State, Manoeuvre
from geometry import Coord
from flightplotting.model import obj, OBJ
from flightanalysis import State
import numpy as np
from typing import List, Union


def plotsec(secs: Union[State, list[State]], scale=5, nmodels=0, fig=None, 
            color: Union[str, list[str]]=None, obj: OBJ=obj, cg=False, width=None, 
            height=None, show_axes=False, ribb: bool=False, tips: bool=True, origin=False):

    traces = []

    if isinstance(secs, State):
        secs = [secs]

    for i, sec in enumerate(secs):
        text = ["{:.1f}".format(val) for val in sec.data.index]
        _color = color if not color is None else px.colors.qualitative.Plotly[i]
        if ribb:
            traces += ribbon(sec, scale * 1.85, _color)
        if tips:
            traces += tiptrace(sec, scale * 1.85, text=text)
        if nmodels > 0:
            traces += meshes(nmodels, sec, _color, obj.scale(scale))
        if cg:
            traces += cgtrace(sec, text=text, color=_color)

    if origin:
        traces += axestrace(Coord.zero(), 50)

    if fig is None:

        fig = go.Figure(
            data=traces,
            layout=go.Layout(template="flight3d+judge_view", uirevision='foo')
        )
        if show_axes:
            fig.update_layout(
                scene=dict(
                aspectmode='data',
                xaxis=dict(visible=True, showticklabels=True),
                yaxis=dict(visible=True, showticklabels=True),
                zaxis=dict(visible=True, showticklabels=True)
            )
            )
        if not width is None:
            fig.update_layout(width=width)
        if not height is None:
            fig.update_layout(height=height)
    else:
        fig.add_traces(traces)
    return fig



def plotdtw(sec: State, manoeuvres: List[str], span=3):
    fig = go.Figure()

    traces = []#tiptrace(sec, span)

    for i, name in enumerate(manoeuvres):
        try:
            seg = sec.get_man_or_el(name)

            traces += ribbon(seg, span, px.colors.qualitative.Alphabet[i], name)

            traces.append(go.Scatter3d(
                x=seg.pos.x, 
                y=seg.pos.y, 
                z=seg.pos.z,
                mode='lines', 
                line=dict(width=6, color=px.colors.qualitative.Alphabet[i]), 
                name=name
            ))
        except Exception as ex:
            pass
            print("no data for manoeuvre {}, {}".format(name, ex))
    fig = go.Figure(
        data=traces,
        layout=go.Layout(template="flight3d+judge_view"),
    )

    return fig



def create_3d_plot(traces):
    return go.Figure(
        traces,
        layout=go.Layout(template="flight3d+judge_view"))



nb_layout = dict(
    margin=dict(l=5, r=5, t=5, b=1), 
    legend=dict(yanchor="top", xanchor="left", x=0.8, y=0.99)
)


def control_brv_plot(sec, control_inputs = ["aileron", "elevator", "rudder", "throttle"]):
    """create a nice 2d plot showing control inputs and rotational velocities for a section"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_traces(axis_rate_trace(sec, dash="dash"), secondary_ys=np.full(3, False))

    fig.add_traces(control_input_trace(sec), secondary_ys=[True for i in range(4)])

    rvrng = np.ceil(np.degrees(sec.brvel.abs().max().max()) / 180) * 180
    cirng = np.ceil(sec.data.loc[:,control_inputs].abs().max().max() / 50) * 50

    fig.update_layout(
        xaxis=dict(title="time, s"),
        yaxis=dict(title="axis rate deg/s",range=(-rvrng, rvrng)),
        yaxis2=dict(title="control pwm offset, ms",range=(-cirng, cirng)),
        **nb_layout
    )
    return fig


def aoa_brv_plot(sec):
    """create a nice 2d plot showing rotational velocities and angle of attack for a section"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_traces(axis_rate_trace(sec), secondary_ys=np.full(3, False))
    fig.add_traces(aoa_trace(sec, colours=px.colors.qualitative.Plotly[4:]), secondary_ys=np.full(2, True))
    fig.update_layout(
        xaxis=dict(title="Time (s)"),
        yaxis=dict(title="Axis Rate (deg/s)"),
        yaxis2=dict(title="Angle of Attack (deg)"),
        **nb_layout
    )
    return fig


def compare_3d(sec1, sec2):
    fig = make_subplots(1, 2, specs=[[{'type': 'scene'}, {'type': 'scene'}]])
    flowntr = plotsec(sec1, scale=2, nmodels=4).data
    templtr = plotsec(sec2, scale=2, nmodels=4).data

    fig.add_traces(flowntr, cols = [1 for i in range(len(flowntr))], rows=[1 for i in range(len(flowntr))] )
    fig.add_traces(templtr, cols = [2 for i in range(len(templtr))], rows=[1 for i in range(len(templtr))] )
    fig.update_layout(template="flight3d", showlegend=False)
    return fig


def grid3dplot(plots):
    """takes an n*m list of lists of 3d figures, puts them into a n*m subplot grid"""

    nrows = len(plots)
    ncols = len(plots[0])

    fig = make_subplots(
        cols=len(plots[0]),
        rows=len(plots),
        specs=[[{"type": "scene"} for i in range(ncols)] for j in range(nrows)]
    )

    sceneids = ["scene{}".format(i+1) for i in range(ncols*nrows)]
    sceneids[0] = "scene"
    fig.update_layout(**{"scene{}".format(i+1 if i>0 else ""):dict(aspectmode='data') for i in range(ncols*nrows)})
    
    for ir, plotrow in enumerate(plots):
        for ic, plot in enumerate(plotrow):
            fig.add_traces(plot.data, cols=np.full(len(plot.data), ic+1).tolist(), rows=np.full(len(plot.data), ir+1).tolist())
    
    return fig



def plot_analysis(analysis, obj=obj, nmodels=20, scale=4, cg=False, tip=True, fig=None, **kwargs):

    obj = obj.scale(scale)

    fig = go.Figure() if not fig else fig

    if cg:
        fig.add_traces(cgtrace(analysis.body, **kwargs))
    if tip:
        fig.add_traces(tiptrace(analysis.body, scale*1.85))
    
    fig.add_traces(vectors(nmodels, analysis.body, analysis.environment.wind * scale / 3))
    
    fig.add_traces(meshes(nmodels,analysis.judge, "blue", obj))
    fig.add_traces(meshes(nmodels,analysis.wind, "red", obj))
    fig.add_traces(meshes(nmodels,analysis.body, "green", obj))
    
    fig.update_layout(
                scene=dict(
                aspectmode='data',
                xaxis=dict(visible=True, showticklabels=True),
                yaxis=dict(visible=True, showticklabels=True),
                zaxis=dict(visible=True, showticklabels=True)
            ), height=800)
    return fig


axis = dict(
    gridcolor="lightgrey", 
    linewidth=2, 
    linecolor='lightgrey',
    zerolinewidth=2,
    zerolinecolor='lightgrey',
    showline=True
)


aiaa_layout = dict(
    margin=dict(l=1, r=1, t=5, b=1), 
    legend=dict(yanchor="top", xanchor="left", x=0.8, y=0.99),
    font_family="Times New Roman",
    font_size=18,plot_bgcolor='rgba(0,0,0,0)',
 #   xaxis=dict(**axis),
 #   yaxis=dict(range=(-100,700), **axis),
 #   yaxis2=dict(range=(-100/20,700/20), **axis),
)

aiaa_full_width = dict(width=1200,**aiaa_layout)
aiaa_half_width = dict(width=600,**aiaa_layout)

aiaa_axis_rates = dict(
    xaxis=dict(range=(0,1.1), **axis),
    yaxis=dict(range=(-100,700), **axis),
    yaxis2=dict(range=(-100/20,700/20), **axis),
    **aiaa_half_width
)