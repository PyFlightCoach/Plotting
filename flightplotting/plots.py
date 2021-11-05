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
    ribbon
)
    
from flightanalysis import Section
from flightanalysis.schedule import Manoeuvre
from flightplotting.model import obj, OBJ
import numpy as np


def plotsec(sec, scale=5, nmodels=0, fig=None, color="orange", obj: OBJ=obj, width=None, height=None, show_axes=False, ribb: bool=False, tips: bool=True):
    traces = []
    if ribb:
        traces += ribbon(sec, scale * 1.85, color)
    
    if tips:
        traces += tiptrace(sec, scale * 1.85)
    
    if nmodels > 0:
        traces += meshes(nmodels, sec, color, obj.scale(scale))

    if fig is None:

        fig = go.Figure(
            data=traces,
            layout=go.Layout(template="flight3d+judge_view")
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


def plotdtw(sec: Section, manoeuvres, span=3):
    fig = go.Figure()

    traces = []#tiptrace(sec, span)

    for i, man in enumerate(manoeuvres):
        try:
            name=man.name
        except AttributeError:
            name = "element {}".format(i)
        
        try:
            seg = man.get_data(sec)
            

            traces += ribbon(seg, span, px.colors.qualitative.Alphabet[i], name)

            traces.append(go.Scatter3d(x=seg.pos.x, y=seg.pos.y, z=seg.pos.z,
                                mode='lines', line=dict(width=6, color=px.colors.qualitative.Alphabet[i]), name=name))
        except Exception as ex:
            print("no data for manoeuvre {}, {}".format(name, ex))
    fig = go.Figure(
        data=traces,
        layout=go.Layout(template="flight3d+judge_view")
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


def control_brv_plot(sec):
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
        xaxis=dict(title="time, s"),
        yaxis=dict(title="axis rate, deg/s"),
        yaxis2=dict(title="angle of attach, deg"),
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