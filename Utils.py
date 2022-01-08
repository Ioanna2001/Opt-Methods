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