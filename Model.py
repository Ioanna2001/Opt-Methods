import csv_reader
import math


class Node:
    """Class that represents a node

    Used either for customers or for the depot

    Attributes:
        id: ID number
        x: X-axis number
        y: Y-axis number
        demand: Customer's demand
        service_time: Customer's required service time
        profit: Profit to be earned from customer
    """
    def __init__(self, id, x, y, demand, service_time, profit):
        self.id = id
        self.x = float(x)
        self.y = float(y)
        self.demand = int(demand)
        self.service_time = int(service_time)
        self.profit = int(profit)
        self.isRouted = False


class Model:
    """Class that represents model of problem

    Attributes:
        allNodes: List of all model nodes
        customers: List of all customers
        max_capacity: Max capacity of vehicles
        max_duration: Max available time for customer service
        vehicles: Available vehicles
        distances: List representing a matrix of all node distances
    """
    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.max_capacity = -1
        self.max_duration = -1
        self.vehicles = -1
        self.distances = []

    def build_model(self):
        self.max_capacity = csv_reader.get_capacity()
        self.max_duration = csv_reader.get_duration()
        self.vehicles = csv_reader.get_vehicles()
        depot = Node(0, csv_reader.get_dx(), csv_reader.get_dy(), 0, 0, 0)
        self.allNodes.append(depot)
        cust_data_lists = csv_reader.get_customer_data()
        custs_map = map(lambda c: Node(int(c['id']), c['x'], c['y'],
                                       c['demand'], c['service_time'], c['profit']), cust_data_lists)
        self.customers.extend(list(custs_map))
        self.allNodes.extend(self.customers)
        self.distances = [[0.0 for x in range(len(self.allNodes))] for y in range(len(self.allNodes))]

        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.distances[i][j] = dist


class Route:
    """Class that represents a vehicle route

    Attributes:
        sequenceOfNodes: List containing order of nodes visited
        profit: Profit earned in route
        capacity: Max capacity of vehicle
        duration: Max available time for customer service
        load: Vehicle load
        travelled: Time spent travelling
    """
    def __init__(self, dp, cap, dur):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.profit = 0
        self.capacity = cap
        self.duration = dur
        self.load = 0
        self.travelled = 0





