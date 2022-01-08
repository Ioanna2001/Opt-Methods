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