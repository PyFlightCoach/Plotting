import plotly.graph_objects as go
import plotting.templates
from geometry import Point, Coord, Transformation
import numpy as np
from plotly.colors import DEFAULT_PLOTLY_COLORS
from flightdata import State
from plotting.model import obj, OBJ
import plotly.express as px


def boxtrace():
    xlim=170*np.tan(np.radians(60))
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


def meshes(npoints, seq: State, colour, scale=1, _obj: OBJ=None):
    _obj = obj if _obj is None else _obj
    if scale != 1:
        _obj = _obj.scale(scale)
    locs = []
    if npoints >= 1:
        locs.append(0)
    if npoints >= 2:
        locs.append(-1)
    if npoints >= 3:
        locs = locs + list(np.cumsum(np.full(npoints-2, len(seq) / (npoints-1))).astype(int))
        
    ms = []
    for loc in locs:
        ms.append(_obj.transform(
            Transformation(seq.pos[loc], seq.att[loc])
        ).create_mesh(colour,f"{seq.time.t[loc]:.1f}"))
    return ms

def vector(origin, direction, **kwargs):
    pdata = Point.concatenate([origin, origin+direction])
    return trace3d(*pdata.data.T, **kwargs)


def vectors(npoints: int, seq: State, vectors: Point, **kwargs):
    trs = []
    step = int(len(seq.data) / (npoints+1))
    for pos, wind in zip(seq.pos[::step], vectors[::step]):
        pdata = Point.concatenate([pos, pos+wind])
        trs.append(trace3d(*pdata.data.T, text=abs(vectors), **kwargs))    
    return trs



def trace3d(datax, datay, dataz, **kwargs):

    if 'mode' not in kwargs:
        kwargs['mode'] = 'lines'
    if kwargs['mode'] == 'lines' and 'line' not in kwargs:
        kwargs['line']=dict(width=2, dash="solid")
    if 'showlegend' not in kwargs:
        kwargs['showlegend'] = False

    return go.Scatter3d(x=datax,y=datay,z=dataz,**kwargs)


def pointtrace(p: Point, **kwargs):
    return trace3d(p.x, p.y, p.z, **kwargs)

def cgtrace(seq, **kwargs):
    return trace3d(
        *seq.pos.data.T,
        **kwargs
    )


def manoeuvretraces(schedule, section: State, colours = px.colors.qualitative.Plotly):
    traces = []
    for man, color in zip(schedule.manoeuvres, colours):
        st = man.get_data(section)
        traces.append(cgtrace(st), color=color, hoverinfo=man.name)

    return traces


def elementtraces(manoeuvre, sec: State):
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



def tiptrace(seq, span, **kwargs):
    
    def make_offset_trace(pos, colour):
        tr =  trace3d(
            *seq.body_to_world(pos).data.T,
            **dict(dict(line=dict(color=colour, width=1)), **kwargs)
        )
        tr['showlegend'] = False
        return tr

    return [
        make_offset_trace(Point(0, span/2, 0), "blue"),
        make_offset_trace(Point(0, -span/2, 0), "red")
    ]


def get_colour(i):
    return DEFAULT_PLOTLY_COLORS[i % len(DEFAULT_PLOTLY_COLORS)]  


def colour_from_scale(v, vmax, scale=px.colors.sequential.Burg):
    return scale[int((len(scale) - 1) * v / vmax)]


def dtwtrace(sec: State, elms, showlegend = True):
    traces = tiptrace(sec, 10)

    

    for i, man in enumerate(elms):
        seg = man.get_data(sec)
        try:
            name=man.name
        except AttributeError:
            name = "element {}".format(i)
        traces.append(
            go.Scatter3d(
                x=seg.pos.x, 
                y=seg.pos.y, 
                z=seg.pos.z,
                mode='lines', 
                line=dict(width=6, color=get_colour(i)), 
                name=name,
                showlegend=showlegend))

    return traces




def axis_rate_traces(sts: dict[str, State], cols='pqr'):
    cols = px.colors.qualitative.D3
    traces = []
    dashes = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    st0 = list(sts.values())[0]
    for i, rv in enumerate(list('pqr')):
        for k, st in sts.items():

            traces.append(go.Scatter(
                x=st0.data.index - st0.data.index[0], y=getattr(st, rv), name=f'{k} {rv}', line=dict(color=cols[i], dash=dashes[list(sts.keys()).index(k)])
            ))
    return traces



def sec_col_trace(sec, columns, dash="solid", colours = px.colors.qualitative.Plotly, yfunc=lambda x: x):
    trs = []
    for i, axis in enumerate(columns):
        trs.append(
            go.Scatter(
                x=sec.data.index, 
                y=yfunc(sec.data[axis]), 
                name=axis, 
                line=dict(color=colours[i], dash=dash)
            ))
    return trs


def axis_rate_trace(sec, dash="solid", colours = px.colors.qualitative.Plotly):
    return sec_col_trace(sec, sec.constructs.rvel.keys, dash, colours, np.degrees) 



control_inputs =  ["aileron_1", "aileron_2", "elevator", "rudder", "throttle"]

def control_input_trace(sec, dash="solid", colours = px.colors.qualitative.Plotly, control_inputs = None):
    if control_inputs is None:
        control_inputs =  ["aileron", "elevator", "rudder", "throttle"]
    return sec_col_trace(sec,control_inputs, dash, colours)


def aoa_trace(sec, dash="dash", colours = px.colors.qualitative.Plotly):
    #sec = sec.append_columns(sec.aoa())
    return sec_col_trace(sec, ["alpha", "beta"], dash, colours, np.degrees)

def axestrace(cid: Coord, length:float=20.0):
    ntraces = []
    colours = {"x":"red", "y":"blue", "z":"green"}
    for i, ci in enumerate(cid):
        for ax, col in zip([ci.x_axis, ci.y_axis, ci.z_axis], list("xyz")):
            axis = Point.concatenate([ci.origin, ci.origin + ax * length])
            ntraces.append(go.Scatter3d(
                x=axis.x, y=axis.y, z=axis.z, mode="lines", 
                line=dict(color=colours[col]),
                name=col,
                showlegend=True if i==0 else False
            ))
        
    return ntraces




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


def ribbon(sec: State, span: float, color, **kwargs):
    """TODO make the colouring more generic
    """

    left = sec.body_to_world(Point(0, span/2, 0))
    right = sec.body_to_world(Point(0, -span/2, 0))

    points = Point(_npinterzip(left.data, right.data))

    
    _i = np.array(range(len(points) - 2))   # 1 2 3 4 5

    _js = np.array(range(1, len(points), 2))
    _j = _npinterzip(_js, _js)[1:-1] # 1 3 3 4 4 5 

    _ks = np.array(range(2, len(points) -1 , 2))
    _k = _npinterzip(_ks, _ks) # 2 2 4 4 6 6 

    return [go.Mesh3d(
        x=points.x, y=points.y, z=points.z, i=_i, j=_j, k=_k,
        intensitymode="cell",
        facecolor=np.full(len(_i), color),
        **kwargs
    )]
