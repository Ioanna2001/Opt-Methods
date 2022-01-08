import copy

from Testing import TestSolution
from Model import Route
from Utils import (CalculateRouteDuration, CalculateTravelledTime, CalculateTotalDuration,
                        UpdateRouteCostAndLoad, CapacityIsViolated)


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
        - moveDistance: Change in distance covered
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
        self.moveDistance = -1

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
        - moveDistance: `float`
        """
        self.originRoutePosition = rt1
        self.targetRoutePosition = rt2
        self.originNodePosition = nd1
        self.targetNodePosition = nd2
        self.durChangeOriginRt = dur1
        self.durChangeTargetRt = dur2
        self.moveDistance = mvd


class SwapMove(object):
    """Represents LocalSearch operation: SwapMove

    SwapMove is a 1 - 1 exchange of nodes. Two nodes exchange
    positions and optionally routes (sequences of nodes).

    Attributes:
        - positionOfFirstRoute: Route number of first node
        - positionOfSecondRoute: Route number of second node
        - positionOfFirstNode: Position number of first node
        - positionOfSecondNode: Position number of second node
        - profitChangeFirstRt: Change of first route's total profit, if the exchange is applied
        - profitChangeSecondRt: Change of second route's total profit, if the exchange is applied
        - moveProfit: Change in profit earned
    """
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.profitChangeFirstRt = None
        self.profitChangeSecondRt = None
        self.moveProfit = -1

    def Initialize(self, rt1, rt2, nd1, nd2, pr1, pr2, mvp):
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
        self.profitChangeFirstRt = pr1
        self.profitChangeSecondRt = pr2
        self.moveProfit = mvp


class TwoOptMove(object):
    """Represents LocalSearch operation: TwoOptMove

    TwoOptMove deletes and creates 2 arcs between 2 routes, to avoid crossover and
    maximize profit.

    Attributes:
        positionOfFirstRoute: Route number of first node
        positionOfSecondRoute: Route number of second node
        positionOfFirstNode: Position number of first node
        positionOfSecondNode: Position number of second node
        moveProfit: Change in profit earned

    """
    def __init__(self):
        """Default constructor

        [extended_summary]
        """
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveProfit = 0

    def Initialize(self, positionOfFirstRoute, positionOfSecondRoute, positionOfFirstNode, positionOfSecondNode, moveProfit):
        """Full constructor

        Inits fields to argument values

        Args:
            positionOfFirstRoute: `int`
            positionOfSecondRoute: `int`
            positionOfFirstNode: `int`
            positionOfSecondNode: `int`
            moveProfit: `int`
        """
        self.positionOfFirstRoute = positionOfFirstRoute
        self.positionOfSecondRoute = positionOfSecondRoute
        self.positionOfFirstNode = positionOfFirstNode
        self.positionOfSecondNode = positionOfSecondNode
        self.moveProfit = moveProfit


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
                                    rt2.travelled + CalculateRouteDuration(self.distanceMatrix, rt2, B) > rt2.duration: #add duration constraint
                                continue

                        distanceAdded = self.distanceMatrix[A.id][C.id] + self.distanceMatrix[F.id][B.id] + \
                                    self.distanceMatrix[B.id][G.id]
                        distanceRemoved = self.distanceMatrix[A.id][B.id] + self.distanceMatrix[B.id][C.id] + \
                                        self.distanceMatrix[F.id][G.id]

                        originRtDurChange = self.distanceMatrix[A.id][C.id] - self.distanceMatrix[A.id][B.id] - \
                                                self.distanceMatrix[B.id][C.id]
                        targetRtDurChange = self.distanceMatrix[F.id][B.id] + self.distanceMatrix[B.id][G.id] - \
                                                self.distanceMatrix[F.id][G.id]

                        moveDistance = distanceAdded - distanceRemoved

                        if (moveDistance < self.relocationMove.moveDistance):
                            return self.relocationMove.Initialize(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                                targetNodeIndex, originRtDurChange,
                                                                targetRtDurChange, moveDistance)
    
    def FindBestSwapMove(self) -> SwapMove:
        for firstRouteIndex in range(0, len(self.solution.routes)):
            rt1: Route = self.solution.routes[firstRouteIndex]
            for secondRouteIndex in range(firstRouteIndex, len(self.solution.routes)):
                rt2: Route = self.solution.routes[secondRouteIndex]
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

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][b2.id] + \
                                                self.distanceMatrix[b2.id][c2.id]
                                costAdded = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][b1.id] + \
                                            self.distanceMatrix[b1.id][c2.id]
                                moveCost = costAdded - costRemoved
                            else:

                                costRemoved1 = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][c1.id]
                                costAdded1 = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][c1.id]
                                costRemoved2 = self.distanceMatrix[a2.id][b2.id] + self.distanceMatrix[b2.id][c2.id]
                                costAdded2 = self.distanceMatrix[a2.id][b1.id] + self.distanceMatrix[b1.id][c2.id]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        else:
                            if rt1.load - b1.demand + b2.demand > self.constraints['capacity']:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.constraints['capacity']:
                                continue

                            costRemoved1 = self.distanceMatrix[a1.id][b1.id] + self.distanceMatrix[b1.id][c1.id]
                            costAdded1 = self.distanceMatrix[a1.id][b2.id] + self.distanceMatrix[b2.id][c1.id]
                            costRemoved2 = self.distanceMatrix[a2.id][b2.id] + self.distanceMatrix[b2.id][c2.id]
                            costAdded2 = self.distanceMatrix[a2.id][b1.id] + self.distanceMatrix[b1.id][c2.id]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        if moveCost < self.swapMove.moveCost:
                            return SwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                costChangeFirstRoute, costChangeSecondRoute, moveCost)

    def FindBestTwoOptMove(self) -> TwoOptMove:
        for rtInd1 in range(0, len(self.solution.routes)):
            rt1: Route = self.solution.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.solution.routes)):
                rt2: Route = self.solution.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        moveCost = 10 ** 9

                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            costAdded = self.distanceMatrix[A.id][K.id] + self.distanceMatrix[B.id][L.id] #change to durations
                            costRemoved = self.distanceMatrix[A.id][B.id] + self.distanceMatrix[K.id][L.id]
                            moveCost = costAdded - costRemoved
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue

                        if moveCost < self.twoOptMove.moveCost:
                            return TwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost) #change to durations

    def ApplyRelocationMove(self):

        rm = self.relocationMove

        oldDuration = CalculateTotalDuration(self.solution)

        originRt = self.solution.routes[rm.originRoutePosition]
        targetRt = self.solution.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if (rm.originNodePosition < rm.targetNodePosition):
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.travelled += rm.moveDistance
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.travelled = CalculateTravelledTime(originRt)
            targetRt.travelled = CalculateTravelledTime(targetRt)
            originRt.load -= B.demand
            targetRt.load += B.demand

        newDuration = CalculateTotalDuration(self.solution)
        # debuggingOnly
        if abs((newDuration - oldDuration) - rm.moveDistance) > 0.0001:
            print('Cost Issue')

    def ApplySwapMove(self):

        sm = self.swapMove

        oldCost = CalculateTotalCost(self.solution)  # TODO Implement inside Utils.py
        rt1 = self.solution.routes[sm.positionOfFirstRoute]
        rt2 = self.solution.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if (rt1 == rt2):
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand

        self.solution.cost += sm.moveCost

        newCost = CalculateTotalCost(self.solution)  # TODO Implement inside Utils.py
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')

    def ApplyTwoOptMove(self): #apply to durations

        top = self.twoOptMove

        rt1: Route = self.solution.routes[top.positionOfFirstRoute]
        rt2: Route = self.solution.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            # reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode]
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            # lst = list(reversedSegment)
            # lst2 = list(reversedSegment)
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment

            # reversedSegmentList = list(reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1]))
            # rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegmentList

            rt1.cost += top.moveCost

        else:
            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]

            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            UpdateRouteCostAndLoad(self.distanceMatrix, rt1)
            UpdateRouteCostAndLoad(self.distanceMatrix, rt2)

        self.solution.cost += top.moveCost

    def run(self):

        while not self.terminateSearch:

            # SolDrawer.draw(localSearchIterator, self.solution, self.allNodes)

            # Relocations
            if self.operator == 0:
                self.FindBestRelocationMove()

                if self.relocationMove.originRoutePosition:
                    if self.relocationMove.moveDistance > 0:
                        self.ApplyRelocationMove()
                    else:
                        self.terminateSearch = True
            # Swaps
            elif self.operator == 1:
                self.FindBestSwapMove()

                if self.swapMove.positionOfFirstRoute:
                    if self.swapMove.moveProfit > 0:
                        self.ApplySwapMove()
                    else:
                        self.terminateSearch = True
            # 2OptMoves
            elif self.operator == 2:
                self.FindBestTwoOptMove()

                if self.twoOptMove.positionOfFirstRoute:
                    if self.twoOptMove.moveProfit > 0:
                        self.ApplyTwoOptMove()
                    else:
                        self.terminateSearch = True

            TestSolution(self.initialSolution)

            if (self.initialSolution.profit > self.optimizedSolution.profit):
                self.optimizedSolution = copy.deepcopy(self.initialSolution)

            self.localSearchIterator = self.localSearchIterator + 1

        return self.optimizedSolution
