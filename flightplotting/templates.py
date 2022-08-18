
import plotly.graph_objects as go
import plotly.io as pio

pio.templates["flight3d"] = go.layout.Template(layout=go.Layout(
    margin=dict(l=0, r=0, t=0, b=0),
    scene=dict(
        aspectmode='data',
        #xaxis=dict(visible=True, showticklabels=True),
        #yaxis=dict(visible=True, showticklabels=True),
        #zaxis=dict(visible=True, showticklabels=True),
    ),
    legend=dict(
        font=dict(size=20),
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
))


pio.templates["judge_view"] = go.layout.Template(layout=go.Layout(scene_camera=dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=-0.2),
    eye=dict(x=0.0, y=-3, z=-0.8),
    projection=dict(type='perspective')
)))
