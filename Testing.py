import matplotlib.pyplot as plt

from Model import Route

def TestSolution(solution):
    totalSolProfit = 0
    for r in range(0, len(solution.routes)):
        rt: Route = solution.routes[r]
        rtProfit = 0
        rtLoad = 0
        for n in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[n]
            rtProfit += A.profit #change to profit
            rtLoad += A.demand
        if abs(rtProfit - rt.profit) < 0.0001: #change operator
            print('Route Profit problem')
        if rtLoad != rt.load:
            print('Route Load problem')

        totalSolProfit += rt.profit

    if abs(totalSolProfit - solution.profit) < 0.0001: #change operator
        print('Solution Profit problem')
    
def ReportSolution(solution, allNodes):
    print("Best solution")
    for i in range(0, len(solution.routes)):
        rt = solution.routes[i]
        print("=== Route " + str(i) + " ===")
        print("load: " + str(rt.load))
        print("duration: " + str(rt.travelled))
        for j in range(0, len(rt.sequenceOfNodes)):
            print(rt.sequenceOfNodes[j].id, end=' ')
        print("\nRoute profit:", rt.profit)
    SolDrawer.draw('ClarkeWright', solution, allNodes)
    print("Total profit:", solution.profit)

class SolDrawer:
    @staticmethod
    def get_cmap(n, name='hsv'):
        return plt.cm.get_cmap(name, n)

    @staticmethod
    def draw(name, sol, nodes):
        plt.clf()
        SolDrawer.drawPoints(nodes)
        SolDrawer.drawRoutes(sol)
        plt.savefig(str(name))

    @staticmethod
    def drawPoints(nodes:list):
        x = []
        y = []
        for i in range(len(nodes)):
            n = nodes[i]
            x.append(n.x)
            y.append(n.y)
        plt.scatter(x, y, c="blue")

    @staticmethod
    def drawRoutes(sol):
        cmap = SolDrawer.get_cmap(len(sol.routes))
        if sol is not None:
            for r in range(0, len(sol.routes)):
                rt = sol.routes[r]
                for i in range(0, len(rt.sequenceOfNodes) - 1):
                    c0 = rt.sequenceOfNodes[i]
                    c1 = rt.sequenceOfNodes[i + 1]
                    plt.plot([c0.x, c1.x], [c0.y, c1.y], c=cmap(r))

