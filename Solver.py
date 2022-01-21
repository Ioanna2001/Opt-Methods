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
        self.rcl_size = 3

    def solve(self):
        for seed in range(10, 60, 10):
            sol = self.MinimumInsertions(itr=seed, foundSolution=None)
            if self.overallBestSol == None or self.overallBestSol.profit < sol.profit:
                self.overallBestSol = copy.copy(sol)
        ReportSolution("MinInsertions", self.overallBestSol, self.allNodes)
        print()
        print("MinInsertions")
        self.overallBestSol.duration = CalculateTotalDuration(self.distanceMatrix, self.overallBestSol)
        print("duration before vns")
        print(self.overallBestSol.duration)
        self.overallBestSol = VNS(self.overallBestSol, 2, self.distanceMatrix)
        print("duration after vns")
        self.overallBestSol.duration = CalculateTotalDuration(self.distanceMatrix, self.overallBestSol)
        print(self.overallBestSol.duration)
        print()
        print("Overall Best")
        ReportSolution("Overall", self.overallBestSol, self.allNodes)
        exportSolution("solution", self.overallBestSol)
        return self.overallBestSol

    def NearestNeighbor(self, itr=30) -> Solution:
        solution = Solution()
        solution.routes.append(Route(self.depot, self.capacity, self.duration))
        pool = set(self.customers)

        vehiclesUsed = 1
        while vehiclesUsed <= 6:
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
                solution.profit += rt.profit
                solution.duration += rt.travelled
                vehiclesUsed += 1
                if len(solution.routes) < 6:
                    solution.routes.append(Route(self.depot, self.capacity, self.duration))

        return solution 

    def FindBestNN(self, pool: list[Node], route: Route, itr) -> Node:
        rng = random.Random(itr)
        rcl: list[RandomCandidate] = []
        for cust in pool:
            if route.load + cust.demand <= route.capacity and \
                AppendNodeDuration(self.distanceMatrix, route, cust) \
                + route.travelled <= route.duration:

                trialProfit = cust.profit / \
                    math.pow(AppendNodeDuration(self.distanceMatrix, route, cust), 0.9)
                
                candidate = RandomCandidate(cust, trialProfit, route, route.sequenceOfNodes[-1])

                # Update rcl list
                if len(rcl) <= self.rcl_size:
                    rcl.append(candidate)
                    rcl.sort(key=lambda x: x.trialProfit)
                elif candidate.trialProfit > rcl[0].trialProfit - 0.001:
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
            sequences = list(map(lambda x: x.sequenceOfNodes, foundSolution.routes))
            routedCustomers = set().union(*sequences)
            pool = pool.difference(routedCustomers)
            solution.routes.extend(foundSolution.routes)
        else:
            solution.routes.append(Route(self.depot, self.capacity, self.duration))

        termination = False
        while not termination:

            candidate = self.FindBestInsertion(pool, solution.routes, itr)
            if candidate:  # Found insertion
                insertCust = candidate.customer
                rt = candidate.route
                pos = candidate.insertionPosition
                # Apply insertion
                rt.sequenceOfNodes.insert(pos, insertCust)
                rt.load += insertCust.demand
                rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
                rt.profit += insertCust.profit
                pool.remove(insertCust)
            else:  # No possible insertion
                if len(solution.routes) < 6:
                    solution.routes.append(Route(self.depot, self.capacity, self.duration))
                else:
                    termination = True

        for r in solution.routes:
            solution.duration += r.travelled
            solution.profit += r.profit

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
                        trialProfit = math.pow(Dp, 1) / math.pow(Dc, 0.6)

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