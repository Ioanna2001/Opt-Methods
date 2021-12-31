from Model import Model
from Solver import *

model = Model()
model.build_model()
s = Solver(model)
sol = s.solve()
