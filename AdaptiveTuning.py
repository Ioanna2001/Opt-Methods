from http.client import NOT_EXTENDED
import numpy as np
import itertools

minInsDenominator = 0.6
minInsNumerator = 1
nnDenominator = 0.9
nnNumerator = 1
precision = 0.0001
exponents = [x for x in np.arange(0.1, 1.5, 0.1)]
precisionList = [0.1, 0.01, 0.001, 0.0001]
rclSize = 4
tuningIterator = 0
noTuningLeft = False

combinations = [x for x in itertools.product(exponents, repeat=2)]

def TuneExponents():
    global tuningIterator, minInsDenominator, minInsNumerator, noTuningLeft
    den, num = combinations[tuningIterator]
    minInsDenominator = den
    minInsNumerator = num
    tuningIterator += 1
    if tuningIterator >= len(combinations) - 1:
        return True
