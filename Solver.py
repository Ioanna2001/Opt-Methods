<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
import random, copy, collections
=======
import random, copy
>>>>>>> parent of 2230256 ([WIP] Add Clarke & Wright algorithm)
=======
import random, copy
>>>>>>> parent of 2230256 ([WIP] Add Clarke & Wright algorithm)
=======
import random, copy
>>>>>>> parent of 2230256 ([WIP] Add Clarke & Wright algorithm)

from Model import *
from Utils import *
from Testing import *
from Optimization import LocalSearch



class Solution:
    """Represents found solution

    Attributes:
        - profit: Profit number
        - routes: List containing vehicle routes
    """
    def __init__(self):
        self.profit = 0.0
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
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.distances
        self.capacity = int(m.max_capacity)
        self.duration = int(m.max_duration)
        self.vehicles = int(m.vehicles)
        self.constraints = {"capacity": self.capacity, "duration": self.duration, "vehicles": self.vehicles}
        self.sol = None
        self.overallBestSol = None
        self.rcl_size = 3

    def solve(self):
        for i in range(5):  # Maybe the range needs change
            self.ClarkWright()
            self.ApplyNearestNeighborMethod(i)
            cc = self.sol.profit
            if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
                self.overallBestSol = copy.deepcopy(self.sol)

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
        print("Overall Best")
        ReportSolution(self.sol)
        return self.sol

    def ApplyNearestNeighborMethod(self, itr=0):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        while (insertions < self.vehicles): #Stops when all routes max duration and capacity is reached
            bestInsertion = CustomerInsertion()
            lastOpenRoute: Route = GetLastOpenRoute(self.sol)

            if lastOpenRoute is not None:
                self.IdentifyBest_NN_ofLastVisited(bestInsertion, lastOpenRoute, itr)
            if (bestInsertion.customer is not None):
                    self.ApplyCustomerInsertion(bestInsertion)
            else:
                # If there is an empty available route
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
                    modelIsFeasible = False
                    break
                else:
                    rt = Route(self.depot, self.capacity, self.duration)
                    self.sol.routes.append(rt)
                    insertions += 1

        if (modelIsFeasible == False):
            print('FeasibilityIssue')
            # reportSolution

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

    def IdentifyBest_NN_ofLastVisited(self, bestInsertion, rt, itr=10):
        random.seed(itr)
        rcl = []
        #the rcl list holds the 3 NearestNeighbor nodes with the best profit
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    if CalculateRouteDuration(self.distanceMatrix, rt, candidateCust) + rt.travelled <= rt.duration:
                        lastNodePresentInTheRoute = rt.sequenceOfNodes[-2] #check if candidates duration fits
                        trialProfit = candidateCust.profit
                        # Update rcl list
                        if len(rcl) < self.rcl_size:
                            new_tup = (trialProfit, candidateCust, rt)
                            rcl.append(new_tup)
                            #rcl[-1] holds the NN node with the best profit so far
                            rcl.sort(key=lambda x: x[0])
                        elif trialProfit > rcl[-1][0]:
                            rcl.pop(len(rcl) - 1)
                            new_tup = (trialProfit, candidateCust, rt)
                            rcl.append(new_tup)
                            rcl.sort(key=lambda x: x[0])
        if len(rcl) > 0:
            #which one of the three will be inserted is picked randomly
            tup_index = random.randint(0, len(rcl) - 1)
            tpl = rcl[tup_index]
            bestInsertion.profit = tpl[0] 
            bestInsertion.customer = tpl[1]
            bestInsertion.route = tpl[2]

    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)
        profitAdded = insCustomer.profit 
        rt.profit += profitAdded
        self.sol.profit += profitAdded
        rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
        rt.load += insCustomer.demand
        insCustomer.isRouted = True

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
        rt.load += insCustomer.demand
        rt.travelled = CalculateTravelledTime(self.distanceMatrix, rt)
        insCustomer.isRouted = True

class SavingsObject():
    def __init__(self):
        self.i = None
        self.j = None
        self.distanceSaved = 0

    def ClarkeWright(self):

        # Create routes for each customer
        routes = []
        for c in self.customers:
            route = Route()
            route.sequenceOfNodes.insert(1, c)
            route = Route(self.depot, self.capacity, self.duration)
            route.sequenceOfNodes.insert(1, c)
            route.load = c.demand
            route.travelled = CalculateRouteDuration(self.distanceMatrix, route, c)
            routes.append(route)

        # Create savings matrix
        savings = []
        for i in range(len(self.customers) - 1):
            for j in range(i + 1, len(self.customers)):
                distanceRemoved = self.distanceMatrix[0][i] + self.distanceMatrix[j][0]
                distanceAdded = self.distanceMatrix[i][j]
                s = SavingsObject()
                s.i = self.customers[i]
                s.j = self.customers[j]
                s.distanceSaved = distanceAdded - distanceRemoved
                savings.append(s)
        savings.sort()

    def ClarkeWrightConditions(routes: list[Route], i: Node, j: Node) -> bool:

        # Find routes where i and j are included
        for route in routes:
            if i in route:
                rt1 = route
            elif j in route:
                rt2 = route

        # Check if i and j are in the same route
        if rt1 == rt2:
            return False

        # Check if i and j are either at the start or at
        # the end of their routes
        nodeInd1 = rt1.index(i)
        if nodeInd1 != 1 and nodeInd1 != rt1[-2]:
            return False

        nodeInd2 = rt2.index(j)
        if nodeInd2 != 1 and nodeInd2 != rt2[-2]:
            return False

        # Check for capacity violation
        if CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
            return False

        # Check for time violation

        # All conditions so far are met
        return True



