#transportation problem
#base on the code of Rodion Chachura https://medium.com/@geekrodion

import os
import re
import sys
import copy
import argparse

class TransportationProblem:
    def __init__(self, supply, demand, cost):
        self.supply = supply
        self.demand = demand
        self.cost = cost
        #to verify the cost dimensions (supply x demand)

class TransportationCell:
    def __init__(self, isBasic, flow):
        self.isBasic = isBasic
        self.flow = flow

    def __str__(self):
        if self.isBasic:
            return f"flow={self.flow}"
        else:
            return f"tmp={self.flow}"

def loadQueueProblemFromFile(filePath):
    supply = []
    demand = []
    cost = []
    with open(filePath, newline='') as dataFile:
        supply = __loadSupplyDemandData(dataFile, "supply=")
        demand = __loadSupplyDemandData(dataFile, "demand=")
        next(dataFile)#costLine
        for s in range(len(supply)):
            line = next(dataFile)
            data = line.split()
            row = [int(i) for i in data]
            cost.append(row)
        return TransportationProblem(supply, demand, cost)
        
def __loadSupplyDemandData(dataFile, text):
    result = []
    textLine = next(dataFile)
    amount = int(textLine.replace(text, ''))
    for i in range(amount):
        line = next(dataFile)
        result.append(int(line))
    return result

        
#transportation Procedure
def getBalance(prob):
    s = sum(prob.supply)
    d = sum(prob.demand)
    if s == d:#the problem is balanced
        return prob
    elif s > d: #add virtual demand node
        newdemand = prob.demand
        newdemand.append(s-d)
        newCost = prob.cost
        for row in newCost:
            row.append(0)
        return TransportationProblem(prob.supply, newdemand, newCost)
    else: # d > s #add virtual suppy node
        newsupply = prob.supply
        newsupply.append(d-s)
        newCost = prob.cost
        row = [0]*len(prob.demand)
        newCost.append(row)
        return TransportationProblem(newsupply, prob.demand, newCost)

def northwestBasicFeasibleSolution(prob):
    supplyAvailable = copy.copy(prob.supply)
    demandAvailable = copy.copy(prob.demand)
    basic = []
    i = 0
    j = 0
    while (i < len(supplyAvailable) and j < len(demandAvailable)):
        v = min(supplyAvailable[i], demandAvailable[j])
        basic.append(((i,j),v))
        supplyAvailable[i] -= v
        demandAvailable[j] -= v
        if supplyAvailable[i] == 0:
            i += 1
        if demandAvailable[j] == 0:
            j +=1
    return __transformBasicToSolution(basic, len(supplyAvailable), len(demandAvailable)) 

def __transformBasicToSolution(basic, supplyLen, demandLen):
    solution = []
    for i in range(supplyLen):
        row = [TransportationCell(False, 0)]*demandLen
        solution.append(row)
    for ((i,j),v) in basic:
        solution[i][j] = TransportationCell(True, v)
    return solution

def getMarginalCost(prob, solution):
    supplyCost = [None]*len(prob.supply)
    demandCost = [None]*len(prob.demand)
    supplyCost[0] = 0
    solIndex = getSolutionIndex(solution)
    while(len(solIndex) > 0):
        for index, (i,j) in enumerate(solIndex):
            if supplyCost[i] is None and demandCost[j] is None:
                continue
            #in this point supply or demand cost has been already assigned
            cost = prob.cost[i][j]
            if supplyCost[i] is None:
                supplyCost[i] = cost - demandCost[j]
            else: 
                demandCost[j] = cost - supplyCost[i]
            solIndex.pop(index)
            break
    return supplyCost, demandCost

def fillNonBasicCells(prob,solution, supplyCost, demandCost):
    enteringIndex = None
    level = 0
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            if not solution[i][j].isBasic:
                cost = supplyCost[i] + demandCost[j] - prob.cost[i][j]
                solution[i][j] = TransportationCell(False, cost)
                if cost > 0:
                    if enteringIndex is None or cost > level:
                        enteringIndex = (i,j)
                        level = cost
    return solution, enteringIndex

def canBeClosedAdding(loop, newItem):
    if len(loop) + 1 < 4:
        return False
    firstItem = loop[0]
    return firstItem[0] == newItem[0] or firstItem[1] == newItem[1] #same row or column

def getNextPossiblePositions(loop, solution, current):
    x,y = current
    results = []
    #next in column
    for j in range(len(solution[x])):
        if j == y or not solution[x][j].isBasic: 
            continue
        #in this point is a basic solution
        if not inLoop(loop, (x,j)):
            results.append((x,j))
    #next in row
    for i in range(len(solution)):
        if i == x or not solution[i][y].isBasic:
            continue
        #in this point is a basic solution
        if not inLoop(loop, (i,y)):
            results.append((i,y))
    return results

def inLoop(loop, current):
    for i,j in loop:
        if i == current[0] and j == current[1]:
            return True
    return False

def getLoop(solution, loop, current):
    nextNodes = getNextPossiblePositions(loop, solution, current)
    if len(nextNodes) == 0:
        return None
    for nextItem in nextNodes:
        if not __canBeAdd(loop, nextItem):
            continue
        close = canBeClosedAdding(loop, nextItem)
        if close:
            newLoop = loop + [nextItem]
            return newLoop
        newLoop = getLoop(solution, loop + [nextItem], nextItem)
        if newLoop:
            return newLoop

def __canBeAdd(loop, nextItem):
    x = 0
    y = 0
    for item in loop:
        if item[0] == nextItem[0]:
            x += 1
        if item[1] == nextItem[1]:
            y += 1
    return x<2 and y<2


def getNewBasicSolution(solution, loop):
    odd = loop[1::2]
    minx, miny = min(odd, key=lambda x: solution[x[0]][x[1]].flow)
    theta = solution[minx][miny].flow
    basic = []
    even = True
    for i,j in loop:
        currentFlow = 0
        if solution[i][j].isBasic:
            currentFlow = solution[i][j].flow
        if even:
            even = False
            basic.append(((i,j),currentFlow + theta))
        else:
            even = True
            if minx == i and miny == j:
                continue
            basic.append(((i,j),currentFlow - theta))
    basic = __completeBase(solution, basic, (minx, miny))
    return __transformBasicToSolution(basic, len(solution), len(solution[1]))
    
def __completeBase(solution, basic, leaving):
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            if i == leaving[0] and j == leaving[1]:
                continue
            if solution[i][j].isBasic:
                if not __isInBase(basic, (i,j)):
                    basic.append(((i,j),solution[i][j].flow))
    return basic

def __isInBase(basic, item):
    for x in basic:
        if x[0][0] == item[0] and x[0][1] == item[1]:
            return True
    return False

def improvementSteps(basic, prob):
    supply, demand = getMarginalCost(prob, basic)
    sol, enteringIndex = fillNonBasicCells(prob, basic, supply, demand)
    while enteringIndex: # the current solution is not optimal
        loop = getLoop(sol, [enteringIndex],enteringIndex)
        newSol = getNewBasicSolution(sol, loop)
        supply, demand = getMarginalCost(prob, newSol)
        sol, enteringIndex = fillNonBasicCells(prob, newSol, supply, demand)
    return sol

def getSolutionIndex(solution):
    index = []
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            if solution[i][j].isBasic:
                index.append((i,j))
    return index

def getCost(prob, solution):
    cost = 0
    for i in range(len(solution)):
        for j in range(len(solution[i])): 
            if solution[i][j].isBasic:
                cost += prob.cost[i][j] * solution[i][j].flow
    return cost

def solve(prob):
    prob = getBalance(prob)
    basic = northwestBasicFeasibleSolution(prob)
    return improvementSteps(basic, prob)

def printSolution(solution):
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            if solution[i][j].isBasic:
                print(f"from {i} to {j} flow={solution[i][j].flow}")

def printSolutionMatrix(solution):
    for i in range(len(solution)):
        row = []
        for j in range(len(solution[i])):
            if solution[i][j].isBasic:
                row.append(f"B={solution[i][j].flow}")
            else:
                row.append(f"{solution[i][j].flow}")
        print(row)

#app
def create_parser():
    parser = argparse.ArgumentParser(prog = "transportation")
    parser.add_argument("-t", "--testFile", type = str, default = "transdata.dat")
    return parser

def printProblem(prob):
    print("supply")
    print(prob.supply)
    print("demand")
    print(prob.demand)
    print("cost")
    print(prob.cost)

def main():
    parser = create_parser()
    args = parser.parse_args()

    prob = loadQueueProblemFromFile(args.testFile)
    sol = solve(prob)
    printSolution(sol)
    print(f"cost={getCost(prob, sol)}")


if __name__ == "__main__":
    main()