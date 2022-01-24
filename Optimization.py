import copy, random

import AdaptiveTuning as tune

from Testing import TestSolution
from Model import (Route, Node)
from Utils import (AppendNodeDuration, CalculateTravelledTime, CalculateTotalDuration,
                        UpdateRouteLoadDurAndProfit, CapacityOrDurationIsViolated)


class RelocationMove(object):
    """Represents LocalSearch operation: Relocation

    Relocation is a 1 - 0 exchange of nodes. A node gets moved to a
    different position, optinally in a different route (sequence of nodes).

    Attributes:
        - originRoutePosition: Original route's number of node to be moved
        - targetRoutePosition: Optional destination route number
        - originNodePosition: Original position's number of node
        - targetNodePosition: Destination position number of node
        - durChangeOriginRt: Change of time spent in original route after deletion of node
        - durChangeTargetRt: Change of time spent in target route after insertion of node
        - moveDur: Change in distance covered
    """

    def __init__(self):
        """Default constructor

        Inits all fields to default values
        """
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.durChangeOriginRt = None
        self.durChangeTargetRt = None
        self.moveDur = 0

    def Initialize(self, rt1, rt2, nd1, nd2, dur1, dur2, mvd):
        """Full constructor

        Inits fields to argument values

        Args:
        - originRoutePosition: `int`
        - targetRoutePosition: `int`
        - originNodePosition: `int`
        - targetNodePosition: `int`
        - durChangeOriginRt: `int`
        - durChangeTargetRt: `int`
        - moveDur: `float`
        """
        self.originRoutePosition = rt1
        self.targetRoutePosition = rt2
        self.originNodePosition = nd1
        self.targetNodePosition = nd2
        self.durChangeOriginRt = dur1
        self.durChangeTargetRt = dur2
        self.moveDur = mvd


class SwapMove(object):
    """Represents LocalSearch operation: SwapMove

    SwapMove is a 1 - 1 exchange of nodes. Two nodes exchange
    positions and optionally routes (sequences of nodes)."""
    
    positionOfFirstRoute = None
    positionOfSecondRoute = None
    positionOfFirstNode = None
    positionOfSecondNode = None
    durChangeFirstRt = None
    durChangeSecondRt = None
    moveDur = 0
    
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.durChangeFirstRt = None
        self.durChangeSecondRt = None
        self.moveDur = 0

    def Initialize(self, rt1, rt2, nd1, nd2, dur1, dur2, mvd):
        """Full constructor

        Inits fields to argument values

        Args:
        - positionOfFirstRoute: `int`
        - positionOfSecondRoute: `int`
        - positionOfFirstNode: `int`
        - positionOfSecondNode: `int`
        - profitChangeFirstRt: `int`
        - profitChangeSecondRt: `int`
        - moveProfit: `int`
        """
        self.positionOfFirstRoute = rt1
        self.positionOfSecondRoute = rt2
        self.positionOfFirstNode = nd1
        self.positionOfSecondNode = nd2
        self.durChangeFirstRt = dur1
        self.durChangeSecondRt = dur2
        self.moveDur = mvd


class TwoOptMove(object):
    """Represents LocalSearch operation: TwoOptMove

    TwoOptMove deletes and creates 2 arcs between 2 routes, to avoid crossover and
    maximize profit.

    Attributes:
        positionOfFirstRoute: Route number of first node
        positionOfSecondRoute: Route number of second node
        positionOfFirstNode: Position number of first node
        positionOfSecondNode: Position number of second node
        moveDur: Duration reduction

    """

    def __init__(self):
        """Default constructor

        [extended_summary]
        """
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveDur = 0

    def Initialize(self, positionOfFirstRoute, positionOfSecondRoute, positionOfFirstNode, positionOfSecondNode, moveDur):
        """Full constructor

        Inits fields to argument values

        Args:
            positionOfFirstRoute: `int`
            positionOfSecondRoute: `int`
            positionOfFirstNode: `int`
            positionOfSecondNode: `int`
            moveDur: `int`
        """
        self.positionOfFirstRoute = positionOfFirstRoute
        self.positionOfSecondRoute = positionOfSecondRoute
        self.positionOfFirstNode = positionOfFirstNode
        self.positionOfSecondNode = positionOfSecondNode
        self.moveDur = moveDur


class LocalSearch:
    """Class for local search operations

    Given an initial solution and values from problem Model,
    applies local search operations to optimize solution.

    Attributes:
        - initialSolution: Initial `Solution` object
        - distanceMatrix: List representing a matrix of all node distances
        - constraints: Dict containing constraints, such as max capacity
        - operator: `int` for selecting MoveType to apply for optimization
        - optimizedSolution: `Solution` optimized
        - localSearchIterator: `int` count of local search applied
        - relocationMove: `RelocationMove`
    """

    def __init__(self, solution, distanceMatrix, constraints, operator):
        """Constructor

        Args:
            solution : `Solution`
            distanceMatrix : `List`
            constraints : `Dict`
            operator : `int`
        """
        self.initialSolution = solution
        self.optimizedSolution = solution
        self.distanceMatrix = distanceMatrix
        self.constraints = constraints
        self.operator = operator
        self.localSearchIterator = 0
        self.relocationMove = RelocationMove()
        self.swapMove = SwapMove()
        self.twoOptMove = TwoOptMove()
        self.terminateSearch = False
        self.allRelocationMoves = list()
        self.allSwapMoves = list()
        self.allTwoOptMoves = list()


    def FindBestRelocationMove(self) -> RelocationMove:

        for originRouteIndex in range(0, len(self.initialSolution.routes)):
            rt1: Route = self.initialSolution.routes[originRouteIndex]
            for targetRouteIndex in range(0, len(self.initialSolution.routes)):
                rt2: Route = self.initialSolution.routes[targetRouteIndex]
                for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):
                        if originRouteIndex == targetRouteIndex and (
                                targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue
                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]
                        if rt1 != rt2:
                            if rt2.load + B.demand > rt2.capacity or \
                                    rt2.travelled + AppendNodeDuration(self.distanceMatrix, rt2, B) > rt2.duration:
                                continue
                        distanceAdded = self.distanceMatrix[A.id][C.id] + self.distanceMatrix[F.id][B.id] + \
                                    self.distanceMatrix[B.id][G.id]
                        distanceRemoved = self.distanceMatrix[A.id][B.id] + self.distanceMatrix[B.id][C.id] + \
                                        self.distanceMatrix[F.id][G.id]
                        originRtDurChange = self.distanceMatrix[A.id][C.id] - self.distanceMatrix[A.id][B.id] - \
                                                self.distanceMatrix[B.id][C.id] - B.service_time
                        targetRtDurChange = self.distanceMatrix[F.id][B.id] + self.distanceMatrix[B.id][G.id] - \
                                                self.distanceMatrix[F.id][G.id] + B.service_time
                        moveDur = distanceAdded - distanceRemoved
                        if rt1 == rt2:
                            if rt1.travelled + moveDur > rt1.duration:
                                continue
                        if moveDur < 0:
                            copyrm = RelocationMove()
                            copyrm.Initialize(originRouteIndex, targetRouteIndex, originNodeIndex,
                                              targetNodeIndex, originRtDurChange,
                                              targetRtDurChange, moveDur)
                            self.allRelocationMoves.append(copyrm)

                        if (moveDur < self.relocationMove.moveDur + tune.precision):
                            self.terminateSearch = False
                            self.relocationMove.Initialize(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                                targetNodeIndex, originRtDurChange,
                                                                targetRtDurChange, moveDur)
                            self.relocationMove
        self.terminateSearch = True

    def FindBestSwapMove(self) -> SwapMove:
        for firstRouteIndex in range(0, len(self.initialSolution.routes)):
            rt1: Route = self.initialSolution.routes[firstRouteIndex]
            for secondRouteIndex in range(firstRouteIndex, len(self.initialSolution.routes)):
                rt2: Route = self.initialSolution.routes[secondRouteIndex]
                for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):
                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]
                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]
                        moveDur = None
                        durChangeFirstRoute = None
                        durChangeSecondRoute = None
                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                durRemoved = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][b2.id] + \
                                                self.distanceMatrix[b2.id][c2.id] 
                                durAdded = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][b1.id] + \
                                            self.distanceMatrix[b1.id][c2.id]  
                                moveDur = durAdded - durRemoved
                            else:
                                durRemoved1 = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][c1.id]
                                durAdded1 = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][c1.id]
                                durRemoved2 = self.distanceMatrix[a2.id][b2.id] + self.distanceMatrix[b2.id][c2.id]
                                durAdded2 = self.distanceMatrix[a2.id][b1.id] + self.distanceMatrix[b1.id][c2.id]
                                moveDur = durAdded1 + durAdded2 - (durRemoved1 + durRemoved2)
                        else:
                            if rt1.load - b1.demand + b2.demand > rt1.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > rt2.capacity:
                                continue
                            durRemoved1 = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][c1.id] + b1.service_time
                            durAdded1 = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][c1.id] + b2.service_time
                            durChangeFirstRoute = durAdded1 - durRemoved1
                            if rt1.duration + durChangeFirstRoute > rt1.duration:
                                continue
                            durRemoved2 = self.distanceMatrix[a2.id][b2.id] + self.distanceMatrix[b2.id][c2.id] + b2.service_time
                            durAdded2 = self.distanceMatrix[a2.id][b1.id] + self.distanceMatrix[b1.id][c2.id] + b1.service_time
                            durChangeSecondRoute = durAdded2 - durRemoved2
                            if rt2.duration + durChangeSecondRoute > rt2.duration:
                                continue
                            moveDur = durChangeSecondRoute + durChangeFirstRoute
                        if moveDur < 0:
                            copys = SwapMove()
                            copys.Initialize(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                             durChangeFirstRoute, durChangeSecondRoute, moveDur)
                            self.allSwapMoves.append(copys)
                        if moveDur < self.swapMove.moveDur:
                            self.swapMove.Initialize(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                durChangeFirstRoute, durChangeSecondRoute, moveDur)
                            self.swapMove
        self.terminateSearch = True


    def FindBestTwoOptMove(self) -> TwoOptMove:
        for rtInd1 in range(0, len(self.initialSolution.routes)):
            rt1: Route = self.initialSolution.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.initialSolution.routes)):
                rt2: Route = self.initialSolution.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2
                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        moveDur = 0
                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]
                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            durAdded = self.distanceMatrix[A.id][K.id] + self.distanceMatrix[B.id][L.id]
                            durRemoved = self.distanceMatrix[A.id][B.id] + self.distanceMatrix[K.id][L.id]
                            moveDur = durAdded - durRemoved
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue
                            if CapacityOrDurationIsViolated(self.distanceMatrix, rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            durAdded = self.distanceMatrix[A.id][K.id] + self.distanceMatrix[B.id][L.id]
                            durRemoved = self.distanceMatrix[A.id][B.id] + self.distanceMatrix[K.id][L.id]
                            moveDur = durAdded - durRemoved
                        if moveDur < 0:
                            copyto = TwoOptMove()
                            copyto.Initialize(rtInd1, rtInd2, nodeInd1, nodeInd2, moveDur)
                            self.allTwoOptMoves.append(copyto)
                        if moveDur < self.twoOptMove.moveDur + tune.precision:
                            self.twoOptMove.Initialize(rtInd1, rtInd2, nodeInd1, nodeInd2, moveDur)
        self.terminateSearch = True

    def ApplyRelocationMove(self):

        rm = self.relocationMove
        oldDuration = CalculateTotalDuration(self.distanceMatrix, self.initialSolution)
        originRt = self.optimizedSolution.routes[rm.originRoutePosition]
        targetRt = self.optimizedSolution.routes[rm.targetRoutePosition]
        B = originRt.sequenceOfNodes[rm.originNodePosition]
        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if (rm.originNodePosition < rm.targetNodePosition):
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.travelled += rm.moveDur
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.travelled = CalculateTravelledTime(self.distanceMatrix, originRt)
            targetRt.travelled = CalculateTravelledTime(self.distanceMatrix, targetRt)
            originRt.load -= B.demand
            targetRt.load += B.demand
        newDuration = CalculateTotalDuration(self.distanceMatrix, self.optimizedSolution)
        if newDuration > oldDuration:
            self.optimizedSolution = copy.copy(self.initialSolution)
        '''
         # debuggingOnly
                if abs((newDuration - oldDuration) - rm.moveDur) > 0.0001:
            print('Cost Issue')
        
        '''

    def ApplySwapMove(self):

        sm = self.swapMove
        oldDuration = CalculateTotalDuration(self.distanceMatrix, self.initialSolution)  # TODO Implement inside Utils.py
        rt1 = self.optimizedSolution.routes[sm.positionOfFirstRoute]
        rt2 = self.optimizedSolution.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1
        if (rt1 == rt2):
            rt1.duration += sm.moveDur
        else:
            rt1.duration += sm.durChangeFirstRt
            rt2.duration += sm.durChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand
        newDuration = CalculateTotalDuration(self.distanceMatrix, self.optimizedSolution)
        if newDuration > oldDuration:
            self.optimizedSolution = copy.copy(self.initialSolution)
        '''
                # debuggingOnly
        if abs((newDur - oldDur) - sm.moveDur) > 0.0001:
            print('Cost Issue')
        '''

    def ApplyTwoOptMove(self):
        top = self.twoOptMove
        oldDuration = CalculateTotalDuration(self.distanceMatrix, self.initialSolution)
        rt1: Route = self.optimizedSolution.routes[top.positionOfFirstRoute]
        rt2: Route = self.optimizedSolution.routes[top.positionOfSecondRoute]
        if rt1 == rt2:
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment
            rt1.duration += top.moveDur

        else:
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]
            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]
            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)
            UpdateRouteLoadDurAndProfit(self.distanceMatrix, rt1)
            UpdateRouteLoadDurAndProfit(self.distanceMatrix, rt2)
        self.optimizedSolution.duration = CalculateTotalDuration(self.distanceMatrix, self.optimizedSolution)
        newDuration = CalculateTotalDuration(self.distanceMatrix, self.optimizedSolution)
        if newDuration > oldDuration:
            self.optimizedSolution = copy.copy(self.initialSolution)

    def run(self):

        while not self.terminateSearch:

            # SolDrawer.draw(localSearchIterator, self.solution, self.allNodes)

            # Relocations
            if self.operator == 0:
                self.FindBestRelocationMove()

                if self.relocationMove.originRoutePosition is not None:
                    if self.relocationMove.moveDur < 0:
                        self.ApplyRelocationMove()
                    else:
                        self.terminateSearch = True
            # Swaps
            elif self.operator == 1:
                self.FindBestSwapMove()

                if self.swapMove.positionOfFirstRoute is not None:
                    if self.swapMove.moveDur < 0:
                        self.ApplySwapMove()
                    else:
                        self.terminateSearch = True
            # 2OptMoves
            elif self.operator == 2:
                self.FindBestTwoOptMove()

                if self.twoOptMove.positionOfFirstRoute is not None:
                    if self.twoOptMove.moveDur < 0:
                        self.ApplyTwoOptMove()
                    else:
                        self.terminateSearch = True

      #      TestSolution(self.initialSolution)

            if (self.initialSolution.duration < self.optimizedSolution.duration):
                self.optimizedSolution = copy.copy(self.initialSolution)

            self.localSearchIterator = self.localSearchIterator + 1

        return self.optimizedSolution

def NeighbourhoodChange(s, ss, k: int):
    '''
    Method to change neighbourhood based on local search operators

    Parameters:
    s: Initial solution
    ss: test solution
    k: operator index
    '''
    if ss.duration < s.duration:
        s = copy.copy(ss)
        k = 0
    else:
        k += 1
    return s, k

def Shake(s, k: int, distanceMatrix):
    '''
    Method to pick random solution generated by k local search operator

    Parameters:
    s: initial solution
    k: local search operator
    '''
    random.seed(30)
    ls = LocalSearch(s, distanceMatrix, None, k)
    lsInitial = LocalSearch(s, distanceMatrix, None, k)
    ls.run()
    solutions = None
    ss = None
    if k == 0:
        solutions = ls.allRelocationMoves
        if len(solutions) > 0:
            indx = random.randint(0, len(solutions) - 1)
            lsInitial.relocationMove = solutions[indx]
            lsInitial.ApplyRelocationMove()
            ss = lsInitial.optimizedSolution
        else:
            return s
    if k == 1:
        solutions = ls.allSwapMoves
        if len(solutions) > 0:
            indx = random.randint(0, len(solutions) - 1)
            lsInitial.swapMove = solutions[indx]
            lsInitial.ApplySwapMove()
            ss = lsInitial.optimizedSolution
        else:
            return s
    if k == 2:
        solutions = ls.allTwoOptMoves
        if len(solutions) > 0:
            indx = random.randint(0, len(solutions) - 1)
            lsInitial.twoOptMove = solutions[indx]
            lsInitial.ApplyTwoOptMove()
            ss = lsInitial.optimizedSolution
        else:
            return s
    return ss

def BestImprovement(s, distanceMatrix, k: int):
    '''
    Method to find steepest descent for k local search operator

    Parameters:
    s: initial solution
    distanceMatrix: distance matrix for all nodes
    k: local search operator
    '''
    condition = True
    counter = 0
    while (condition):
        ss = copy.copy(s)
        ls = LocalSearch(s, distanceMatrix, None, k)
        ls.run()
        s = ls.optimizedSolution
        counter += 1
        if s.profit >= 1026:
            ys = True
        if (s.duration >= ss.duration):
            break
        elif counter > 20:
            return ss
    return s

def VNS(s, kmax: int, distanceMatrix):
    '''
    Method to apply Basic VNS

    Parameters:
    s: initial solution
    kmax: count of local search operators
    distanceMatrix: distance matrix for all nodes
    '''
    k = 0
    condition = True
    while (condition):
        ss = Shake(s, k, distanceMatrix)
        sss = BestImprovement(ss, distanceMatrix, k)
        s, k = NeighbourhoodChange(s, sss, k)
        if k > kmax:
            break
    return s