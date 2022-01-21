import time

from Model import Model
from Solver import *
from AdaptiveTuning import noTuningLeft, TuneExponents
from Testing import exportSolution, ReportSolution
import solution_checker


start = time.time()

model = Model()
model.build_model()
bestSol = Solver(model).solve()
while not noTuningLeft:
    TuneExponents()
    model.build_model()
    sol: Solution = Solver(model).solve()
    if sol.profit > bestSol.profit:
        bestSol = copy.copy(sol)

ReportSolution("OverallBestSolution", bestSol, model.allNodes)
exportSolution("solution", bestSol)
solution_checker.run()


end = time.time()
print('Seconds elapsed:', end - start)
