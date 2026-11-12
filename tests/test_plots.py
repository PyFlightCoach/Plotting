import plotly.graph_objects as go
import geometry as g
import numpy as np
from flightdata import State
from plotting import plotsec
from plotting.traces import cgtrace
from pytest import fixture


EXPECTED_CG = {
    "x": [1, 2, 3, 4, 5],
    "y": [10, 20, 30, 40, 50],
    "z": [100, 200, 300, 400, 500],
}


def assert_cg_coordinates(trace):
    for axis, expected in EXPECTED_CG.items():
        np.testing.assert_array_equal(getattr(trace, axis), expected)

@fixture
def state():
    time = g.Time.from_t(np.array([0, 0.25, 0.5, 0.75, 1.0]))
    positions = g.Point(
        np.array(
            [
                [1, 10, 100],
                [2, 20, 200],
                [3, 30, 300],
                [4, 40, 400],
                [5, 50, 500],
            ],
            dtype=np.float64,
        )
    )
    transform = g.Transformation.build(positions, g.Q0(len(positions)))
    return State.from_transform(transform, time=time)


def test_plotsec_cg(state):
    fig = plotsec(state, tips=False, cg=True)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert_cg_coordinates(fig.data[0])


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
    assert_cg_coordinates(trace)
