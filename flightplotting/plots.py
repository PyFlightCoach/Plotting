import plotly.graph_objects as go
import flightplotting.templates
from flightplotting.traces import tiptrace, meshes
from flightanalysis import Section
from flightanalysis.schedule import Manoeuvre

def plotsec(sec, obj, scale=10, nmodels=20, fig=None, color="orange"):
    traces = tiptrace(sec, scale * 1.85)
    if nmodels > 0:
        traces += meshes(obj.scale(scale), nmodels, sec, color)

    if fig is None:
        fig = go.Figure(
            data=traces,
            layout=go.Layout(template="flight3d+judge_view")
        )
    else:
        for trace in traces:
            fig.add_trace(trace)
    return fig


def plotdtw(sec: Section, manoeuvres):
    fig = go.Figure()

    traces = tiptrace(sec, 10)

    for i, man in enumerate(manoeuvres):
        seg = man.get_data(sec)
        try:
            name=man.name
        except AttributeError:
            name = "element {}".format(i)
        traces.append(go.Scatter3d(x=seg.pos.x, y=seg.pos.y, z=seg.pos.z,
                               mode='lines', line=dict(width=6), name=name))

    fig = go.Figure(
        data=traces,
        layout=go.Layout(template="flight3d+judge_view")
    )

    return fig



def create_3d_plot(traces):
    return go.Figure(
        traces,
        layout=go.Layout(template="flight3d+judge_view"))
