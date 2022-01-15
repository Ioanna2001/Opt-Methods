from multiprocessing.spawn import get_preparation_data
import random, itertools, copy

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
        #for i in range(1, 6):  # Maybe the range needs change
        self.ClarkeWrightPaessens()
        if self.overallBestSol == None or self.overallBestSol.profit < self.sol.profit:
            self.overallBestSol = copy.deepcopy(self.sol)
        """
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
        """
        self.sol.duration = CalculateTotalDuration(self.distanceMatrix, self.sol)
        print("Overall Best")
        ReportSolution(self.overallBestSol, self.allNodes)
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

    def ClarkeWrightPaessens(self):
        self.sol = Solution()
        
        
        # Paessens (1988) "M4" strategy parameters
        #
        # After several tests, the best parameteres are:
        # g=1.4, f=0.5 
        g_param, f_param = 1.4, 0.5
    
        routes, savings = self.PaessensInit(g_param, f_param)
        
        routes = self.ClarkeWrightAlgo(savings, routes)

        solution = Solution()
        solution.routes = routes
        for r in routes:
            solution.profit += r.profit

        self.sol = solution


            
            
    def PaessensInit(self, g_param: float, f_param: float):
        """Paessens & Clarke-Wright savings algorithm initialization

        This implements the Paessens (1988) variant of the parallel savings
        model of Clarke and Wright (1964). The savings function is 
        parametrized with multipliers g and f:

            S_ij  = c_0i + c_0j - g * c_ij + f * | c_0i - c_0j |
        
        In our case, cost is replaced by profit:

            S_ij = g * p_ij - (p_0i + p_0j) - f * | p_0i - p_0j |

        Args:
            g_param (`float`): g multiplier
            f_param (`float`): f multiplier

        Returns:
            tuple(list[Route], list[SavingsObject]): Savings list & initial routes
        """

        # Create routes for each customer
        routes: list[Route] = []
        for c in self.customers:
            route = Route(self.depot, self.capacity, self.duration)
            route.sequenceOfNodes.insert(1, c)
            route.load = c.demand
            route.travelled = CalculateTravelledTime(self.distanceMatrix, route)
            route.profit = c.profit
            routes.append(route)

        # Create cost matrix
        profitChange = {}
        for pair in itertools.combinations(self.allNodes, 2):
            a: Node = pair[0]
            b: Node = pair[1]
            dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
            profitChange[pair] = b.profit / dist + b.service_time  # TODO Test alternatives

        # Create savings matrix
        savings = []
        for pair in itertools.combinations(self.customers, 2):
            i = pair[0]
            j = pair[1]
            profitRemoved = profitChange[self.depot, i] + profitChange[self.depot, j]
            profitAdded = profitChange[i, j]
            # Savings function
            s_ij = g_param * profitAdded - profitRemoved - f_param \
                    * abs(profitChange[self.depot, i] - profitChange[self.depot, j])
            s = SavingsObject(i, j, s_ij)
            savings.append(s)
        savings.sort(key=lambda x:x.distanceSaved, reverse=True)
        
        return routes, savings

    def ClarkeWrightAlgo(self, savings: list[SavingsObject],
             routes: list[Route], itr=1, rcl_size=1) -> list[Route]:
        """Clarke-Wright algorithm with rcl

        Given savings and routes lists, creates routes according to
        Clarke & Wright algorithm. Random candidate list is included, but
        optional

        Args:
            savings (list[SavingsObject]): Savings list
            routes (list[Route]): Initial routes
            itr (int, optional): Algorithm iterations. Defaults to 1.
            rcl_size (int, optional): Random candidate list. Defaults to 1.

        Returns:
            list[Route]: Solution routes
        """

        rng = random.Random(itr * 10)

        while savings:

            # Create rcl
            rcl: list[SavingsObject] = []
            for s in savings:

                # Check if routes of SavingsObject can be merged
                if not ClarkeWrightConditions(self.distanceMatrix, routes, s.i, s.j):
                    continue
                else:
                    rcl.append(s)

                if len(rcl) == rcl_size:
                    break


            if len(rcl) > 0:
                # Get random saving from Rcl
                randomIndex = rng.randint(0, len(rcl) - 1)
            else:
                # No feasible nodes left
                break

            s = rcl[randomIndex]
            savings.remove(s)

            # fist node
            i = s.i
            # second node
            j = s.j

            # Find routes of nodes
            for r in routes:

                if i in r.sequenceOfNodes:
                    rt1: Route = r
                elif j in r.sequenceOfNodes:
                    rt2: Route = r

            # Figure out which node should go first
            if rt2.sequenceOfNodes[1] != j and rt1.sequenceOfNodes[-2] != i:
                # swap nodes
                i, j = j, i
                # swap routes
                rt1, rt2 = rt2, rt1

            # Remove route to be merged
            routes.remove(rt2)
            # Remove depot from second route
            rt2.sequenceOfNodes.pop(0)
            # Remove depot from first route
            rt1.sequenceOfNodes.pop()
            #merge routes
            rt1.sequenceOfNodes.extend(rt2.sequenceOfNodes)
            rt1.load += rt2.load
            rt1.travelled = CalculateTravelledTime(self.distanceMatrix, rt1)
            rt1.profit += rt2.profit

        routes.sort(key=lambda x: x.profit, reverse=True)
        output = []
        for i in range(0, 6):
            output.append(routes[i])
        return output
