import plotly.graph_objects as go
import flightplotting.templates
from .model import OBJ
from geometry import Point, Coord
import numpy as np
from typing import List, Union
from math import cos, sin, tan, radians
from geometry import Points
from flightanalysis import Section
from flightanalysis.schedule import Manoeuvre, Schedule


def boxtrace():
    xlim=170*tan(radians(60))
    ylim=170
    return [go.Mesh3d(
        #  0  1     2     3      4    5      6
        x=[0, xlim, 0,    -xlim, xlim, 0,   -xlim], 
        y=[0, ylim, ylim,  ylim, ylim, ylim, ylim], 
        z=[0, 0,    0,     0,    xlim, xlim, xlim], 
        i=[0, 0, 0, 0, 0], 
        j=[1, 2, 1, 3, 4], 
        k=[2, 3, 4, 6, 6],
        opacity=0.4
    )]


def meshes(obj, npoints, seq, colour):
    start = seq.data.index[0]
    end = seq.data.index[-1]
    return [
        obj.transform(
            seq.get_state_from_time(
                start + (end-start) * i / npoints
            ).transform
        ).create_mesh(
            colour,
            "{:.1f}".format(start + (end-start) * i / npoints)
        ) for i in range(0, npoints+1)
    ]


def trace3d(datax, datay, dataz, colour='black', width=2, text=None, name="trace3d"):
    return go.Scatter3d(
        x=datax,
        y=datay,
        z=dataz,
        line=dict(color=colour, width=width),
        mode='lines',
        text=text,
        hoverinfo="text",
        name=name
    )


def cgtrace(seq, name="cgtrace"):
    return trace3d(
        *seq.pos.to_numpy().T,
        colour="black",
        text=["{:.1f}".format(val) for val in seq.data.index],
        name=name
    )

def manoeuvretraces(schedule: Schedule, section: Section):
    traces = []
    for man in schedule.manoeuvres:
        manoeuvre = man.get_data(section)
        traces.append(go.Scatter3d(
            x=manoeuvre.x,
            y=manoeuvre.y,
            z=manoeuvre.z,
            mode='lines',
            text=manoeuvre.element,
            hoverinfo="text",
            name=man.name
        ))

    return traces


def elementtraces(manoeuvre: Manoeuvre, sec: Section):
    traces = []
    for id, element in enumerate(manoeuvre.elements):
        elm = element.get_data(sec)
        traces.append(go.Scatter3d(
            x=elm.x,
            y=elm.y,
            z=elm.z,
            mode='lines',
            text=manoeuvre.name,
            hoverinfo="text",
            name=str(id)
        ))

    return traces



def tiptrace(seq, span):
    text = ["{:.1f}".format(val) for val in seq.data.index]

    def make_offset_trace(pos, colour, text):
        tr =  trace3d(
            *seq.body_to_world(pos).data.T,
            colour=colour,
            text=text,
            width=1
        )
        tr['showlegend'] = False
        return tr

    return [
        make_offset_trace(Point(0, span/2, 0), "blue", text),
        make_offset_trace(Point(0, -span/2, 0), "red", text)
    ]


def axis_rate_trace(sec, ab = False):
    if ab:
        return [
            go.Scatter(x=sec.data.index, y=abs(sec.brvr), name="r"),
            go.Scatter(x=sec.data.index, y=sec.brvp, name="p"),
            go.Scatter(x=sec.data.index, y=abs(sec.brvy), name="y")]
    else:
        return [
            go.Scatter(x=sec.data.index, y=sec.brvr, name="r"),
            go.Scatter(x=sec.data.index, y=sec.brvp, name="p"),
            go.Scatter(x=sec.data.index, y=sec.brvy, name="y")]


def _axistrace(cid):
    return trace3d(*cid.get_plot_df(20).to_numpy().T)

def axestrace(cids: Union[Coord, List[Coord]]):
    if isinstance(cids, List):
        return [_axistrace(cid) for cid in cids]
    elif isinstance(cids, Coord):
        return _axistrace(cids)



def _npinterzip(a, b):
    """
    takes two numpy arrays and zips them.
    Args:
        a ([type]): [a1, a2, a3]
        b ([type]): [b1, b2, b3]

    Returns:
        [type]: [a1, b1, a2, b2, a3, b3]
    """
    assert(len(a) == len(b))
    assert(a.dtype == b.dtype)
    if a.ndim == 2:
        c = np.empty((2*a.shape[0], a.shape[1]), dtype=a.dtype)
        c[0::2, :] = a
        c[1::2, :] = b
    elif a.ndim == 1:
        c = np.empty(2*len(a), dtype=a.dtype)
        c[0::2] = a
        c[1::2] = b

    return c


def ribbon(sec: Section, span: float):
    """WIP Vectorised version of ribbon, borrowed from kdoaij/FlightPlotting

        refactoring ribbon, objectives:
            speed it up by avoiding looping over array - done
            make the colouring more generic - not yet
        minor mod - 2 triangles per pair of points: - done
            current pair to next left
            current right to next pair
        
    """

    left = sec.body_to_world(Point(0, span/2, 0))
    right = sec.body_to_world(Point(0, -span/2, 0))

    points = Points(_npinterzip(left.data, right.data))

    triids = np.array(range(points.count - 2))
    _i = triids   # 1 2 3 4 5

    _js = np.array(range(1, points.count, 2))
    _j = _npinterzip(_js, _js)[1:-1] # 1 3 3 4 4 5 

    _ks = np.array(range(2, points.count -1 , 2))
    _k = _npinterzip(_ks, _ks) # 2 2 4 4 6 6 

    return [go.Mesh3d(
        x=points.x, y=points.y, z=points.z, i=_i, j=_j, k=_k,
        intensitymode="cell",
        #facecolor=np.full(len(triids), "red"),
        #showlegend=True,
        hoverinfo="none"
    )]
