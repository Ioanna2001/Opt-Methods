from Model import Route, Node

def CalculateRouteDuration(distanceMatrix, rt: Route, targetNode: Node) -> float:
    lastRouteNode = rt.sequenceOfNodes[-2].id
    destinationNode = targetNode.id
    originToTargetDistance = distanceMatrix[lastRouteNode][destinationNode]
    targetToDepotDistance = distanceMatrix[destinationNode][0]
    timeTravelled = originToTargetDistance + targetNode.service_time + targetToDepotDistance
    return timeTravelled

def CalculateTravelledTime(distanceMatrix, rt: Route) -> float:
    travelled = 0.0
    for i in range(0, len(rt.sequenceOfNodes) - 1):
        A = rt.sequenceOfNodes[i].id
        B = rt.sequenceOfNodes[i + 1].id
        travelled += distanceMatrix[A][B]
        travelled += rt.sequenceOfNodes[i + 1].service_time
    return travelled

def ReportSolution(solution):
    print("Best solution")
    for i in range(0, len(solution.routes)):
        rt = solution.routes[i]
        print("Route " + str(i))
        print("load: " + str(rt.load))
        print("duration: " + str(rt.travelled))
        for j in range(0, len(rt.sequenceOfNodes)):
            print(rt.sequenceOfNodes[j].id, end=' ')
        print("Route profit")
        print(rt.profit)
    print("Total profit")
    print(solution.profit)

def GetLastOpenRoute(solution) -> int:
    if len(solution.routes) == 0:
        return None
    else:
        return solution.routes[-1]

def CalculateTotalDuration(solution) -> float:
    dur = 0.0
    for i in range(0, len(solution.routes)):
        rt = solution.routes[i]
        dur += CalculateTravelledTime(rt)
    return dur

def UpdateRouteCostAndLoad(distanceMatrix, rt: Route): # update root duration
    tc = rt.sequenceOfNodes[0].service_time
    tl = 0
    for i in range(0, len(rt.sequenceOfNodes) - 1):
        A = rt.sequenceOfNodes[i]
        B = rt.sequenceOfNodes[i + 1]
        tc += distanceMatrix[A.id][B.id] #change to customers profit
        tc += B.service_time
        tl += A.demand
    rt.load = tl
    rt.travelled = tc

def CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2) -> bool:

    rt1FirstSegmentLoad = 0
    for i in range(0, nodeInd1 + 1):
        n = rt1.sequenceOfNodes[i]
        rt1FirstSegmentLoad += n.demand
    rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

    rt2FirstSegmentLoad = 0
    for i in range(0, nodeInd2 + 1):
        n = rt2.sequenceOfNodes[i]
        rt2FirstSegmentLoad += n.demand
    rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

    if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity):
        return True
    if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity):
        return True

def CalculateRouteProfit(route: Route):
    profit = 0
    for c in route.sequenceOfNodes:
        profit += c.profit
    return profit

def ClarkeWrightConditions(distanceMatrix, routes: list[Route], i: Node, j: Node) -> bool:
    # Find routes where i and j are included
    for route in routes:
        if i in route.sequenceOfNodes:
            rt1 = route
        if j in route.sequenceOfNodes:
            rt2 = route

    # Check if i and j are in the same route
    if rt1 == rt2:
        return False

    # Check if i and j are either at the start or at
    # the end of their routes
    nodeInd1 = rt1.sequenceOfNodes.index(i)
    if nodeInd1 != 1 and nodeInd1 != len(rt1.sequenceOfNodes) - 2:
        return False

    nodeInd2 = rt2.sequenceOfNodes.index(j)
    if nodeInd2 != 1 and nodeInd2 != len(rt2.sequenceOfNodes) - 2:
        return False

    # Check for capacity violation
    if CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
        return False

    # Check for time violation
    #copy of rt1 without end depot node
    rt1Unfinished = Route(rt1.sequenceOfNodes[0], rt1.capacity, rt1.duration)
    rt1Unfinished.sequenceOfNodes = rt1.sequenceOfNodes[:len(rt1.sequenceOfNodes) - 1]
    #copy of rt2 without start depot node
    rt2Unfinished = Route(rt2.sequenceOfNodes[0], rt2.capacity, rt2.duration)
    rt2Unfinished.sequenceOfNodes = rt2.sequenceOfNodes[1:]
    #test route to calculate time
    testRoute = Route(rt1.sequenceOfNodes[0], rt1.capacity, rt1.duration)
    testRoute.sequenceOfNodes = rt1Unfinished.sequenceOfNodes + rt2Unfinished.sequenceOfNodes
    if CalculateTravelledTime(distanceMatrix, testRoute) > rt1.duration:
        return False
    # All conditions so far are met
    return True