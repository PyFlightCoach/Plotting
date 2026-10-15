from flightdata import Flight, State
from pytest import fixture
from plotting import plotsec
from plotting.traces import cgtrace
import plotly.graph_objects as go

@fixture
def state():
    return State.from_flight(Flight.from_json('tests/data/p23_flight.json'))


def test_plotsec_cg(state):
    fig = plotsec(state, tips=False, cg=True)
    assert isinstance(fig, go.Figure)


def test_plotsec_legend(state):
    fig = plotsec({"flown": state, "template": state}, tips=False, legend=True)
    legend_traces = [trace for trace in fig.data if trace.showlegend]

    assert [trace.name for trace in legend_traces] == ["flown", "template"]
    assert [trace.marker.symbol for trace in legend_traces] == ["square", "square"]
    assert [trace.marker.color for trace in legend_traces] == ["#636EFA", "#EF553B"]

    fig_without_legend = plotsec(
        {"flown": state, "template": state}, tips=False, legend=False
    )
    assert not any(trace.showlegend for trace in fig_without_legend.data)

def test_cgtrace(state):
    trace = cgtrace(state)
    assert isinstance(trace, go.Scatter3d)