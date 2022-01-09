import time

from Model import Model
from Solver import *

start = time.time()

model = Model()
model.build_model()
s = Solver(model)
sol = s.solve()

end = time.time()
print('Seconds elapsed:', end - start)
