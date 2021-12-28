class Customer:
    def __init__(self, id, x, y, demand, service_time, profit):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.service_time = service_time
        self.profit = profit
        self.visited = False