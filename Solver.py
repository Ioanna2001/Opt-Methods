import random, copy

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

    def __init__(self, customer: Node, profit: float):
        self.customer = customer
        self.trialProfit = profit

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
        self.sol = self.NearestNeighbor()
        if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
            self.overallBestSol = copy.deepcopy(self.sol)
        """
     #  print(i, 'Constr:', self.sol.profit)
        self.MinimumInsertions(i)
        if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
            self.overallBestSol = copy.deepcopy(self.sol)
     #   self.ReportSolution(self.sol)
        optimize = LocalSearch(self.sol, self.distanceMatrix, self.constraints, operator=0)
        self.sol = optimize.run()
        if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
            self.overallBestSol = copy.deepcopy(self.sol)
    #    print(i, 'Const: ', cc, ' LS:', self.sol.profit, 'BestOverall: ', self.overallBestSol.profit)

        self.sol = self.overallBestSol
        """
        # print("Nearest neigbor")
        # self.sol.duration = CalculateTotalDuration(self.distanceMatrix, self.sol)
        # ReportSolution("Nearest neighbour", self.sol, self.allNodes)
        # print("duration before vns")
        # print(self.sol.duration)
        # self.sol = VNS(self.sol, 1, self.distanceMatrix)
        # print("duration after vns")
        # self.sol.duration = CalculateTotalDuration(self.distanceMatrix, self.sol)
        # print(self.sol.duration)
        print("Overall Best")
        ReportSolution("Overall", self.overallBestSol, self.allNodes)
        return self.sol

    def MinimumInsertions(self, itr):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0

        while (insertions < self.vehicles): #Change it to stop when all routes max durations are reached
            bestInsertion = CustomerInsertionAllPositions()
            lastOpenRoute: Route = GetLastOpenRoute(self.sol)

            if lastOpenRoute is not None:
                self.IdentifyBestInsertionAllPositions(bestInsertion, lastOpenRoute, itr)

            if (bestInsertion.customer is not None):
                    self.ApplyCustomerInsertionAllPositions(bestInsertion)
            else:
                # If there is an empty available route
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
                    modelIsFeasible = False
                    break
                # If there is no empty available route and no feasible insertion was identified
                else:
                    rt = Route(self.depot, self.capacity, self.duration)
                    self.sol.routes.append(rt)
                    insertions += 1

        if (modelIsFeasible == False):
            print('FeasibilityIssue')
            # reportSolution

        TestSolution(self.sol)

    def IdentifyBestInsertionAllPositions(self, bestInsertion, rt, itr=10):
        random.seed(itr)
        rcl = []
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    if CalculateRouteDuration(self.distanceMatrix, rt, candidateCust) + rt.travelled <= rt.duration:
                        for j in range(0, len(rt.sequenceOfNodes) - 1):
                            trialProfit = candidateCust.profit

                            if len(rcl) < self.rcl_size:
                                new_tup = (trialProfit, candidateCust, rt, j)
                                rcl.append(new_tup)
                                rcl.sort(key=lambda x: x[0])
                            elif trialProfit < rcl[-1][0]:
                                rcl.pop(len(rcl) - 1)
                                new_tup = (trialProfit, candidateCust, rt, j)
                                rcl.append(new_tup)
                                rcl.sort(key=lambda x: x[0])
        if len(rcl) > 0:
            tup_index = random.randint(0, len(rcl) - 1)
            tpl = rcl[tup_index]
            bestInsertion.profit = tpl[0]
            bestInsertion.customer = tpl[1]
            bestInsertion.route = tpl[2]
            bestInsertion.insertionPosition = tpl[3]

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        rt.profit += insertion.profit
        self.sol.profit += insertion.profit
        self.sol.duration = CalculateTotalDuration(self.sol)
        rt.load += insCustomer.demand
        rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
        insCustomer.isRouted = True


    def NearestNeighbor(self, itr=30) -> Solution:
        solution = Solution()
        solution.routes.append(Route(self.depot, self.capacity, self.duration))
        pool = copy.deepcopy(self.customers)

        while len(solution.routes) <= 6 and pool:
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
                
                candidate = RandomCandidate(cust, trialProfit)

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
