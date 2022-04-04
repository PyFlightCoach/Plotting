from flightanalysis import State, Loop
from geometry import Transformation, Euler, P0
import numpy as np

st = Loop(100, 1, 1).create_template(Transformation(P0(), Euler(np.pi, 0, 0)), 20)


from flightplotting import plotsec

plotsec(st, nmodels=5).show()