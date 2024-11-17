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

def test_cgtrace(state):
    trace = cgtrace(state)
    assert isinstance(trace, go.Scatter3d)