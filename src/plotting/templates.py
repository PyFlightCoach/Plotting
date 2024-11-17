
import plotly.graph_objects as go
import plotly.io as pio

flight3d_template = go.layout.Template(layout=go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    scene=dict(
        aspectmode='data',
    ),
    legend=dict(
        font=dict(size=20),
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
))

pio.templates["flight3d"] = flight3d_template

judges_view_template = go.layout.Template(layout=go.Layout(scene_camera=dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=-0.2),
    eye=dict(x=0.0, y=-3, z=-0.8),
    projection=dict(type='perspective')
)))


pio.templates["judge_view"] = judges_view_template


clean_paper_template = go.layout.Template(layout=go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    scene=dict(
        aspectmode='data',
        xaxis = dict(visible=False),
        yaxis = dict(visible=False),
        zaxis =dict(visible=False)
    ),
    legend=dict(
        font=dict(size=20),
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
))

pio.templates["clean_paper"] = judges_view_template