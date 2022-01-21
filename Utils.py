from Model import Route, Node

def AppendNodeDuration(distanceMatrix: list[int], rt: Route, targetNode: Node) -> float:
    """Calculates duration of visiting new node

    Calculates vehicle's time spent when a new node is added.
    Combines both travelling time and service time of the new node.

    Args:
        distanceMatrix `list[int]`: List representing a matrix of all node distances
        rt `Route`: Specified route
        targetNode `Node`: New node to be appended

    Returns:
        float: duration
    """
    lastRouteNode = rt.sequenceOfNodes[-2].id
    destinationNode = targetNode.id
    originToTargetDistance = distanceMatrix[lastRouteNode][destinationNode]
    targetToDepotDistance = distanceMatrix[destinationNode][0]
    timeTravelled = originToTargetDistance + targetNode.service_time + targetToDepotDistance
    return timeTravelled

def CalculateTravelledTime(distanceMatrix: list[int], rt: Route) -> float:
    """Calculates total time spent in route

    Calculates total duration of route, by combining both travelling and service time.

    Args:
        distanceMatrix `list[int]`: List representing a matrix of all node distances
        rt `Route`: Specified route

    Returns:
        float: time spent
    """
    travelled = 0.0
    for i in range(0, len(rt.sequenceOfNodes) - 1):
        A = rt.sequenceOfNodes[i].id
        B = rt.sequenceOfNodes[i + 1].id
        travelled += distanceMatrix[A][B]
        travelled += rt.sequenceOfNodes[i + 1].service_time
    return travelled

def GetLastOpenRoute(solution) -> int:
    if len(solution.routes) == 0:
        return None
    else:
        return solution.routes[-1]

def CalculateTotalDuration(distanceMatrix, solution) -> float:
    dur = 0.0
    for i in range(0, len(solution.routes)):
        rt = solution.routes[i]
        dur += CalculateTravelledTime(distanceMatrix, rt)
    return dur

def UpdateRouteLoadDurAndProfit(distanceMatrix: list[int], rt: Route):
    """Calculates and updates route's cost and load
    Given a specific route, calculates total load, duration(travelled time) and profit
    Args:
        distanceMatrix `list[int]`: List representing a matrix of all node distances
        rt `Route`: Specified route
    """
    totalDuration = rt.sequenceOfNodes[0].service_time
    totalLoad = 0
    totalProfit = 0
    for i in range(0, len(rt.sequenceOfNodes) - 1):
        A = rt.sequenceOfNodes[i]
        B = rt.sequenceOfNodes[i + 1]
        totalLoad += A.demand
        totalDuration += distanceMatrix[A.id][B.id]
        totalDuration += B.service_time
        totalProfit += A.profit
    rt.load = totalLoad
    rt.travelled = totalDuration
    rt.profit = totalProfit

def CapacityOrDurationIsViolated(distanceMatrix: list[int], rt1: Route, nodeInd1: int, rt2: Route, nodeInd2: int) -> bool:
    """Checks if 2-opt move is going to violate Capacity or Duration restrictions
    
    Given two routes and two nodes check if applying 2-opt move is
     going to violate Capacity or Duration restrictions on either root
    Args:
        distanceMatrix `list[int]`: List representing a matrix of all node distances
        rt1 `Route`: Route 1
        nodeInd1 `int`: Node representing where the first route is going to split
        rt2 `Route`: Route 2
        nodeInd2 `int`: Node representing where the second route is going to split
    Returns:
        boolean: True, if capacity restrictions or duration restrictions are violated
    """
    rt1Duration = rt1.duration - distanceMatrix[rt1.sequenceOfNodes[nodeInd1].id][rt1.sequenceOfNodes[nodeInd1 + 1].id]
    rt1FirstSegmentDuration = 0
    rt1FirstSegmentLoad = 0
    for i in range(0, nodeInd1):
        A = rt1.sequenceOfNodes[i]
        B = rt1.sequenceOfNodes[i + 1]
        rt1FirstSegmentDuration += distanceMatrix[A.id][B.id]
        rt1FirstSegmentDuration += B.service_time
        rt1FirstSegmentLoad += B.demand

    rt1SecondSegmentDuration = rt1Duration - rt1FirstSegmentDuration
    rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad
    rt2Duration = rt2.duration - distanceMatrix[rt2.sequenceOfNodes[nodeInd2].id][rt2.sequenceOfNodes[nodeInd2 + 1].id]
    rt2FirstSegmentDuration = 0
    rt2FirstSegmentLoad = 0
    for i in range(0, nodeInd2):
        K = rt2.sequenceOfNodes[i]
        L = rt2.sequenceOfNodes[i + 1]
        rt2FirstSegmentDuration += distanceMatrix[K.id][L.id]
        rt2FirstSegmentDuration += L.service_time
        rt2FirstSegmentLoad += L.demand

    rt2SecondSegmentDuration = rt2Duration - rt2FirstSegmentDuration
    rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

    if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity) or (rt1FirstSegmentDuration + rt2SecondSegmentDuration > rt1.duration):
        return True
    if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity) or (rt2FirstSegmentDuration + rt1SecondSegmentDuration > rt2.duration):
        return True

def CalculateRouteProfit(route: Route) -> int:
    """Calculates total profit of route

    Args:
        route `Route`: Specified route

    Returns:
        int: total profit
    """
    profit = 0
    for c in route.sequenceOfNodes:
        profit += c.profit
    return profit
