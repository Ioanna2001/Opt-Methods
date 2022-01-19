import random, copy, numpy as np

from Model import *
from Utils import *
from Testing import *
from Optimization import *



class Solution:
    """Represents found solution

    Attributes:
        - profit: Profit number
        - routes: List containing vehicle routes
    """
    def __init__(self):
        self.profit = 0.0
        self.duration = 0.0
        self.routes = []

class CustomerInsertion(object):
    """Represents a node insertion in a route

    To be used for customer nodes

    Attributes:
        - customer: Customer `Node` for insertion
        - route: `Route` for customer to be inserted
        - profit: Profit gained from insertion 
    """

    def __init__(self):
        self.customer = None
        self.route = None
        self.profit = 0


class CustomerInsertionAllPositions(object):
    """Represents a node insertion in a specific
    position of a route

    To be used for customer nodes

    Attributes:
        - customer: Customer `Node` for insertion
        - route: `Route` for customer to be inserted
        - insertionPosition: Position number for insertion
        - profit: Profit gained from insertion 
    """
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.profit = 0

class SavingsObject():
    """Represents the distance saved is two nodes are merged

        To be used for Clarke-Wright

        Attributes:
            - i: start node
            - j: end node
            - distanceSaved: the total distance saved by the merge
        """

    def __init__(self):
        self.i = None
        self.j = None
        self.distanceSaved = 0

    def __init__(self, i, j, distanceSaved):
        self.i = i
        self.j = j
        self.distanceSaved = distanceSaved

class RandomCandidate:

    def __init__(self, customer: Node, trialProfit: float, \
            route: Route, insertionPosition: int):

        self.customer = customer
        self.trialProfit = trialProfit
        self.route = route
        self.insertionPosition = insertionPosition

class Solver:
    """Class to solve built problem model

    Attributes:
        - allNodes: List of all model nodes
        - customers: List of all nodes representing customers
        - depot: Depot node
        - distanceMatrix: List representing a matrix of all node distances
        - capacity: Max capacity of vehicles
        - duration: Max available time for customer service
        - vehicles: Available vehicles
        - sol: current `Solution`
        - overallBestSol: Overall best `Solution`
        - rcl_size: Number of elements to be used in restricted candidate list
    """

    def __init__(self, m):
        self.allNodes: list[Node] = m.allNodes
        self.customers: list[Node] = m.customers
        self.depot: Node = m.allNodes[0]
        self.distanceMatrix = m.distances
        self.capacity = int(m.max_capacity)
        self.duration = int(m.max_duration)
        self.vehicles = int(m.vehicles)
        self.constraints = {"capacity": self.capacity, "duration": self.duration, "vehicles": self.vehicles}
        self.sol: Solution = None
        self.overallBestSol: Solution = None
        self.rcl_size = 1

    def solve(self):
        for seed in range(10, 60, 10):
            self.sol = self.MinimumInsertions(itr=seed)
            if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
                self.overallBestSol = copy.deepcopy(self.sol)
        ReportSolution("MinInsertions", self.overallBestSol, self.allNodes)
        print()
        print("MinInsertions")
        self.sol.duration = CalculateTotalDuration(self.distanceMatrix, self.sol)
        print("duration before vns")
        print(self.sol.duration)
        self.overallBestSol = VNS(self.overallBestSol, 0, self.distanceMatrix)
        print("duration after vns")
        self.sol.duration = CalculateTotalDuration(self.distanceMatrix, self.sol)
        print(self.sol.duration)
        print()
        print("Overall Best")
        self.overallBestSol = copy.deepcopy(self.sol)
        ReportSolution("Overall", self.overallBestSol, self.allNodes)
        exportSolution("solution", self.overallBestSol)
        return self.sol

    def NearestNeighbor(self, itr=30) -> Solution:
        solution = Solution()
        solution.routes.append(Route(self.depot, self.capacity, self.duration))
        pool = copy.deepcopy(self.customers)

        while len(solution.routes) <= 6:
            rt = solution.routes[-1]

            insertCust = self.FindBestNN(pool, rt, itr)
            if insertCust:
                # before the second occurence of depot
                insIndex = len(rt.sequenceOfNodes) - 1
                rt.sequenceOfNodes.insert(insIndex, insertCust)
                rt.profit += insertCust.profit
                rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
                rt.load += insertCust.demand
                pool.remove(insertCust)

            else:
                solution.routes.append(Route(self.depot, self.capacity, self.duration))
                solution.profit += rt.profit
                solution.duration += rt.travelled

        solution.routes.pop()
        return solution 

    def FindBestNN(self, pool: list[Node], route: Route, itr) -> Node:
        rng = random.Random(itr)
        rcl: list[RandomCandidate] = []
        for cust in pool:
            if route.load + cust.demand <= route.capacity and \
                CalculateRouteDuration(self.distanceMatrix, route, cust) \
                + route.travelled <= route.duration:

                trialProfit = cust.profit / \
                    math.pow(CalculateRouteDuration(self.distanceMatrix, route, cust), 0.9)
                
                candidate = RandomCandidate(cust, trialProfit, route, route.sequenceOfNodes[-1])

                # Update rcl list
                if len(rcl) <= self.rcl_size:
                    rcl.append(candidate)
                    rcl.sort(key=lambda x: x.trialProfit)
                elif candidate.trialProfit > rcl[0].trialProfit:
                    rcl.pop(0)
                    rcl.append(candidate)
                    rcl.sort(key=lambda x: x.trialProfit)
        if len(rcl) == 0:
            return  # No fit candidates left

        # Choose a candidate randomly
        candidateIndex = rng.randint(0, len(rcl) - 1)
        return rcl[candidateIndex].customer


    def MinimumInsertions(self, itr=30, foundSolution: Solution = None) -> Solution:
        """Implements insertions algorithm

        Can both build a solution from scratch, as well as improve a given solution.

        Args:
            itr (`int`, optional): Seed to use in rng. Defaults to 30.
            foundSolution (`Solution`, optional): Already found solution. Defaults to None.

        Returns:
            Solution: Solution found with algorithm
        """
        pool = set(self.customers)
        solution = Solution()

        if foundSolution:
            routedCustomers = set().union(*foundSolution.routes)
            pool = pool.difference(routedCustomers)
            solution.routes = foundSolution.routes
        else:
            solution.routes.append(Route(self.depot, self.capacity, self.duration))

        routesChecked = 0
            
        while routesChecked < 6:
            rt = solution.routes[routesChecked]

            candidate = self.FindBestInsertion(pool, solution.routes, itr)
            if candidate:  # Found insertion
                insertCust = candidate.customer
                rt = candidate.route
                pos = candidate.insertionPosition
                # Apply insertion
                candidate.customer.isRouted = True
                rt.sequenceOfNodes.insert(pos, insertCust)
                rt.load += insertCust.demand
                rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
                rt.profit += insertCust.profit
                pool.remove(insertCust)
            else:  # No possible insertion
                solution.profit += rt.profit
                solution.duration += rt.travelled
                routesChecked += 1
                if len(solution.routes) < 6:
                    solution.routes.append(Route(self.depot, self.capacity, self.duration))

        return solution

    def FindBestInsertion(self, pool: set[Node], routes: list[Route], itr) -> RandomCandidate:
        rng = random.Random(itr)
        rcl: list[RandomCandidate] = []
        for cust in pool:

            for route in routes:

                # Check capacity constraint & PART of time constraint
                if route.load + cust.demand <= route.capacity and \
                    cust.service_time + route.travelled <= route.duration:

                    for pos in range(len(route.sequenceOfNodes) - 1):
                        A: Node = route.sequenceOfNodes[pos]
                        B: Node = route.sequenceOfNodes[pos + 1]

                        
                        costAdded = self.distanceMatrix[A.id][cust.id] + \
                            self.distanceMatrix[cust.id][B.id] + cust.service_time
                        costRemoved = self.distanceMatrix[A.id][B.id]
                        Dc = costAdded - costRemoved

                        # Check time constraint fully
                        if route.travelled + Dc > route.duration:
                            continue

                        Dp = cust.profit
                        trialProfit = Dp / math.pow(Dc, 0.6)

                        candidate = RandomCandidate(cust, trialProfit, route, pos + 1)
                        # Update rcl list
                        if len(rcl) <= self.rcl_size:
                            rcl.append(candidate)
                            rcl.sort(key=lambda x: x.trialProfit)
                        elif candidate.trialProfit > rcl[0].trialProfit - 0.001:
                            rcl.pop(0)
                            rcl.append(candidate)
                            rcl.sort(key=lambda x: x.trialProfit)
        if len(rcl) == 0:
            return None  # No fit candidates left

        # Choose a candidate randomly
        candidateIndex = rng.randint(0, len(rcl) - 1)
        return rcl[candidateIndex]