import csv_reader
import math
import itertools

class Node:

    def __init__(self, id, x, y, demand, service_time, profit):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.service_time = service_time
        self.profit = profit
        self.visited = False


class Model:
    # Instance variables
    def __init__(self):
        self.all_nodes = []  # List of all model nodes
        self.customers = []  # List of all customers
        self.max_capacity = -1  # Max capacity
        self.max_duration = -1  # Max duration
        self.vehicles = -1  # Available vehicles
        self.distances = dict()  # Dict containing all distances from one node to another

    def build_model(self):
        self.max_capacity = csv_reader.get_capacity()
        self.max_duration = csv_reader.get_duration()
        self.vehicles = csv_reader.get_vehicles()
        depot = Node(0, csv_reader.get_dx(), csv_reader.get_dy(), 0, 0)
        self.all_nodes.append(depot)
        customers = csv_reader.get_customer_data()
        self.all_nodes.extend(customers)
        self.customers.extend(customers)

        # Dict keys are all possible combinations of 2 nodes, without repetition
        for key in itertools.combinations(self.customers, 2):
            a = key[0]
            b = key[1]
            # Dict values are the distances
            dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
            self.distances[key] = dist
