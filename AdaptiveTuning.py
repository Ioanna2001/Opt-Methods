import numpy as np
import itertools

minInsDenominator = 0.6
minInsNumerator = 1
nnDenominator = 0.9
nnNumerator = 1
precision = 0.0001
exponents = [x for x in np.arange(0.1, 1.5, 0.1)]
rclSize = 3
tuningIterator = 0
noTuningLeft = False

combinations = [x for x in itertools.product(exponents, repeat=2)]

def TuneExponents():
    global tuningIterator, minInsDenominator, minInsNumerator, noTuningLeft
    num, den = combinations[tuningIterator]
    minInsDenominator = den
    minInsNumerator = num
    tuningIterator += 1
    if tuningIterator >= len(combinations) - 1:
        return True