from plotting.model import OBJ
from plotting import plotsec
from flightdata import State

obj = OBJ.load_model("placebo.obj")

st = State.from_transform()

plotsec(st,  model=obj).show()