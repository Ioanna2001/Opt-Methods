import time

from Model import Model
from Solver import *
import solution_checker

start = time.time()

model = Model()
model.build_model()
s = Solver(model)
sol = s.solve()
solution_checker.run()


end = time.time()
print('Seconds elapsed:', end - start)
