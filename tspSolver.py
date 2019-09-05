import os
import sys
import math
import copy
import random
import matplotlib.pyplot as plt

def loadTSPfromFile(filePath):
    data = []
    with open(filePath, newline='') as dataFile:
        next(dataFile) #header line
        for line in dataFile:
            r = line.split()
            data.append([float(r[1]), float(r[2])])
    return TSPProblem(data)

class TSPProblem:
    def __init__(self,tspData):
        self.data = tspData

    def distance(self, x, y):
        """
            x,y valid index
        """
        xn = self.data[x]
        yn = self.data[y]
        return math.sqrt(math.pow(xn[0]-yn[0],2) + math.pow(xn[1]-yn[1],2))

    def getCost(self, tour):
        cost = 0
        for i in range(len(tour)):
            next = i+1 if i+1 < len(tour) else 0
            cost += self.distance(tour[i], tour[next])
        return cost

    def getNearestNodeSolutoin_startingNode(self, x):
        inTour = [False]*len(self.data)
        inTour[x] = True
        nodesToAdd = len(self.data)-1
        cost = 0
        current = x
        tour = [x]
        while nodesToAdd > 0:
            n = self.getNearestNode(current, inTour)
            tour.append(n[0])
            cost += n[1]
            current = n[0]
            inTour[current]=True
            nodesToAdd -=1
        #clossing tour
        cost += self.distance(current, x)
        return tour, cost

    def getNearestNode(self, current, inTour):
        nextNodes = self.getCandidateList(current, inTour)
        return min(nextNodes, key=lambda n: n[1])
    
    def getCandidateList(self, current, inTour):
        candidates = []
        for i in range(len(self.data)):
            if not inTour[i]:
                candidates.append([i, self.distance(current, i)])
        return candidates

    def getNearestNodeSolution_multistart(self):
        nodes = []
        for i in range(len(self.data)):
            t,c = self.getNearestNodeSolutoin_startingNode(i)
            nodes.append([i,t,c])
        return min(nodes, key=lambda s:s[2])

    def getGreedyRandomizeSolution(self, alpha=0.2):
        inTour = [False]*len(self.data)
        startingNode = random.randint(0, len(self.data)-1)
        inTour[startingNode]=True
        nodesToAdd = len(self.data)-1
        current = startingNode
        tour = [startingNode]
        while nodesToAdd > 0:
            candidates = self.getCandidateList(current, inTour)
            rcl = restrictedCandidateList(candidates, alpha)
            n = rcl[random.randint(0, len(rcl)-1)]
            tour.append(n)
            current = n
            inTour[current]=True
            nodesToAdd -=1
        return tour

    def plot_nodes(self):
        plt.clf()
        x = [d[0] for d in self.data]
        y = [d[1] for d in self.data]
        plt.plot(x,y, "or")
        plt.savefig("tsp_nodes.png")

    def plot_tour(self, tour, fileName):
        plt.clf()
        x = []
        y = []
        for n in tour:
            x.append(self.data[n][0])
            y.append(self.data[n][1])
        #clossing tour
        x.append(self.data[tour[0]][0])
        y.append(self.data[tour[0]][1])
        plt.plot(x,y,"or")
        plt.plot(x,y)
        plt.savefig(fileName)

    def local_move(self, tour, improvement):
        """
        improvement = FI or BI
        """
        if len(tour) <= 2: #the tour does not change
            return tour
        bestCost = 0
        node = -1
        possition = -1
        for i in range(len(self.data)):
            for j in range(i+1,len(self.data)): #move node tour[i] to possition j where j > i
                deltaCost = self.getMoveCost(tour, i,j)
                if deltaCost < bestCost:
                    bestCost = deltaCost
                    node = i
                    possition = j
                    if improvement == "FI":
                        return self.doMove(tour, node, possition)
        if bestCost < 0:
            return self.doSwapMove(tour, node, possition)
        else:
            return tour

    def getMoveCost(self, tour, xpos, ypos):
        if xpos == 0 and ypos == len(tour)-1: #the tour does not change
            return 0
        b_xpos = xpos-1 if xpos > 0 else len(tour)-1
        a_xpos = xpos+1 if xpos+1 < len(tour) else 0
        a_ypos = ypos+1 if ypos+1 < len(tour) else 0
        #removing edges
        dellEdges = self.distance(tour[b_xpos], tour[xpos]) + self.distance(tour[xpos], tour[a_xpos]) #removing adjecent edge to x
        dellEdges += self.distance(tour[ypos], tour[a_ypos])
        #adding edges
        addEdges = self.distance(tour[b_xpos], tour[a_xpos]) #reconecting the tour
        addEdges += self.distance(tour[ypos], tour[xpos]) + self.distance(tour[xpos], tour[a_ypos])
        return addEdges - dellEdges

    def doMove(self, tour, xpos, ypos):
        node = tour.pop(xpos)
        if ypos < len(tour):
            tour.insert(ypos, node)
        else:
            tour.append(node)
        return tour

    def local_swap(self, tour, improvement):
        """
        improvement = FI or BI
        """
        if len(tour) <= 2: #the tour does not change
            return tour
        bestCost = 0
        xpos = -1
        ypos = -1
        for i in range(len(self.data)):
            for j in range(i+1, len(self.data)): #swap node tour[i] with node tour[j] where j > i
                deltaCost = self.getSwapCost(tour, i,j)
                if deltaCost < bestCost:
                    bestCost = deltaCost
                    xpos = i
                    ypos = j
                    if improvement == "FI":
                        return self.doSwapMove(tour, xpos, ypos)
        if bestCost < 0:
            return self.doSwapMove(tour, xpos, ypos)
        else:
            return tour


    def getSwapCost(self, tour, xpos, ypos):
        if xpos+1 == ypos or (xpos == 0 and ypos == len(tour)-1):
            #nonconsecutive swap and extreme swap (0 with n)
            return self.getConsecutiveSwapCost(tour, xpos, ypos)
        else:
            #nonconsecutive swap
            return self.getNonConsecutiveSwapCost(tour, xpos, ypos)
    
    def getNonConsecutiveSwapCost(self, tour, xpos, ypos):
        b_xpos = xpos-1 if xpos > 0 else len(tour)-1
        a_xpos = xpos+1 if xpos+1 < len(tour) else 0
        b_ypos = ypos-1 if ypos > 0 else len(tour)-1
        a_ypos = ypos+1 if ypos+1 < len(tour) else 0
        dellEdges = self.distance(tour[b_xpos], tour[xpos]) + self.distance(tour[xpos], tour[a_xpos])
        dellEdges += self.distance(tour[b_ypos], tour[ypos]) + self.distance(tour[ypos], tour[a_ypos])
        addEdges = self.distance(tour[b_xpos], tour[ypos]) + self.distance(tour[ypos], tour[a_xpos])
        addEdges += self.distance(tour[b_ypos], tour[xpos]) + self.distance(tour[xpos], tour[a_ypos])
        return addEdges - dellEdges
 
    def getConsecutiveSwapCost(self, tour, xpos, ypos):
        if xpos+1 != ypos:#extreme case swap 0 with n-1
            tmp = xpos
            xpos = ypos
            ypos = tmp
        b_xpos = xpos-1 if xpos > 0 else len(tour)-1
        a_ypos = ypos+1 if ypos+1 < len(tour) else 0
        dellEdges = self.distance(tour[b_xpos], tour[xpos]) + self.distance(tour[ypos], tour[a_ypos])
        addEdgest = self.distance(tour[b_xpos], tour[ypos]) + self.distance(tour[xpos], tour[a_ypos])
        return addEdgest - dellEdges

    def doSwapMove(self, tour, xpos, ypos):
        tmp = tour[xpos]
        tour[xpos] = tour[ypos]
        tour[ypos] = tmp
        return tour

    def local_2opt(self, tour, improvement):
        if len(tour) <= 2:#the tour does not change
            return 0
        bestCost = 0
        xpos = -1
        ypos = -1
        for i in range(len(self.data)-2):
            for j in range(i+2, len(self.data)):#can not remove to consecutive edges
                deltaCost = self.get2OptDeltaCost(tour, i,j)
                if deltaCost < bestCost:
                    bestCost = deltaCost
                    xpos = i
                    ypos = j
                    if improvement == "FI":
                        return self.do2OptMove(tour, xpos, ypos)
        if bestCost < 0:
            return self.do2OptMove(tour, xpos, ypos)
        else:
            return tour

    def get2OptDeltaCost(self, tour, xpos, ypos):
        a_xpos = xpos+1 if xpos+1 < len(tour) else 0
        a_ypos = ypos+1 if ypos+1 < len(tour) else 0
        dellEdges = self.distance(tour[xpos], tour[a_xpos]) + self.distance(tour[ypos], tour[a_ypos])
        addEdges = self.distance(tour[xpos], tour[ypos]) + self.distance(tour[a_xpos], tour[a_ypos])
        return addEdges -  dellEdges

    def do2OptMove(self, tour, xpos, ypos):
        #it is assumed that xpos < ypos
        if ypos + 1 == len(tour):
            tour[xpos + 1 :] =  tour[-1:xpos:-1]
        else:
            tour[xpos + 1: ypos+1] = tour[ypos:xpos:-1]
        return tour

    #ga procedures
    def generateRandomItem(self, costFnc):
        tour = [i for i in range(len(self.data))]
        random.shuffle(tour)
        return tour, costFnc(tour)

    def orderCrossoverOneSide(self, xTour, yTour):
        x = 0
        y = 0
        while x==y:
            x = random.randint(0,len(self.data)-1)
            y = random.randint(0,len(self.data)-1)
        leftPoint = min(x,y)
        rightPoint = max(x,y)
        print(f"l={leftPoint} r={rightPoint}")
        tour = [-1]*len(self.data)
        inTour = [False]*len(self.data)
        #fill center
        for i in range(leftPoint, rightPoint+1, 1):
            tour[i] = xTour[i]
            inTour[tour[i]] = True
        #fill the rest
        parentIndex = rightPoint+1 if rightPoint + 1 < len(self.data) else 0
        offspringIndex = parentIndex
        nodesToAdd = len(self.data) - rightPoint + leftPoint - 1 #len - (right - left + 1)
        while nodesToAdd > 0:
            pNode = yTour[parentIndex]
            if inTour[pNode]:
                parentIndex = parentIndex + 1 if parentIndex + 1 < len(self.data) else 0
                continue
            else:
                tour[offspringIndex] = yTour[parentIndex]
                inTour[tour[offspringIndex]] = True
                nodesToAdd -= 1
                parentIndex = parentIndex + 1 if parentIndex + 1 < len(self.data) else 0
                offspringIndex = offspringIndex + 1 if offspringIndex + 1 < len(self.data) else 0
        return tour



def localSearchProcedure(solution, neighborStrategy, explorationCnd):
    while True:
        tmp = copy.copy(solution)
        newSol = neighborStrategy(tmp, explorationCnd)
        if newSol == solution:
            return newSol
        else:
            solution = newSol

def variableNeighborhoodDescendant(solution, neigborStrategyList, explorationCnd, costFnc):
    n = 0
    solCost = costFnc(solution)
    while n < len(neigborStrategyList):
        procedure = neigborStrategyList[n]
        tmp = copy.copy(solution)
        newSol = procedure(tmp, explorationCnd)
        newCost = costFnc(newSol)
        if newCost < solCost:
            n = 0
            solution = newSol
            solCost = newCost
        else:
            n += 1
    return solution

def restrictedCandidateList(candidates, alpha):
    rcl = []
    cmin = min(candidates, key=lambda x:x[1])[1]
    cmax = max(candidates, key=lambda x:x[1])[1]
    for c in candidates:
        if c[1] <= cmin + alpha*(cmax-cmin):
            rcl.append(c[0])
    return rcl #rcl contains at least one element, the greedy insertion

def grasp(greedySolFnc, costFnc, localSearchFnc, explorationCnd, maxIter, alpha=0.2):
    bestCost = 1000000000000000000000
    bestSol = None
    for i in range(maxIter):
        sol = greedySolFnc(alpha)
        newSol = localSearchFnc(sol, explorationCnd)
        newCost = costFnc(newSol)
        if newCost < bestCost:
            bestSol = copy.copy(newSol)
    return bestSol

def main():
    tsp = loadTSPfromFile("tspData_6.dat")
    print("Greedy")
    tour, cost = tsp.getNearestNodeSolutoin_startingNode(0)
    print(tour)
    print(cost)
    # tsp.plot_tour(tour, "greedy.png")
    nFnc = [lambda x,e:tsp.local_move(x,e), lambda x,e:tsp.local_swap(x,e), lambda x,e:tsp.local_2opt(x,e)]
    nName = ["localMove.png", "localSwap.png", "local2Opt.png"]
    # for i in range(3):
    #     print(f"Local Search {nName[i]}")
    #     np = nFnc[i]
    #     localtour = localSearchProcedure(tour, np, "BI")
    #     print(localtour)
    #     print(tsp.getCost(localtour))
    #     tsp.plot_tour(localtour, nName[i])
    costFnc = lambda x: tsp.getCost(x)
    # print("VND")
    # vndtour = variableNeighborhoodDescendant(tour, nFnc, "FI", costFnc)
    # print(vndtour)
    # print(tsp.getCost(vndtour))
    # tsp.plot_tour(vndtour, "vnd.png")
    # print("Greedy Randomize Solution")
    # tour = tsp.getGreedyRandomizeSolution()
    # print(tour)
    # print(tsp.getCost(tour))
    # greedyFnc = lambda alpha: tsp.getGreedyRandomizeSolution(alpha)
    # print("GRASP")
    # maxIter = int(len(tsp.data)/2)
    # for i in range(3):
    #    print(f"Local Search {nName[i]}")
    #    tour = grasp(greedyFnc, costFnc, nFnc[i], "FI", maxIter, alpha=0.2)
    #    print(tour)
    #    print(tsp.getCost(tour))
    # print("GRASP + VND")
    # vndFnc = lambda x, improvement: variableNeighborhoodDescendant(x, nFnc, improvement, costFnc)
    # tour = grasp(greedyFnc, costFnc, vndFnc, "FI", maxIter)
    # print(tour)
    # print(tsp.getCost(tour))
    # tsp.plot_tour(tour, "grasp_vnd.png")
    print("GA")
    x=[0,1,2,3,4,5,6]
    random.shuffle(x)
    y=[0,1,2,3,4,5,6]
    random.shuffle(y)
    print(x)
    print(y)
    tour = tsp.orderCrossoverOneSide(x,y)
    print(tour)


    
if __name__ == "__main__":
    main()