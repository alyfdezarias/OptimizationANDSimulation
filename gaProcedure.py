#gaProcedure
import copy
import random

class GAItem:
    def __init__(self, tour, cost):
        self.tour = tour
        self.cost = cost
    
    def __str__(self):
        return f"c={self.cost:.2f} => {self.tour}"

def gaProcedure(populationNum, maxIterations, cities, costFnc, localSearchFnc, crProb=0.9, mtProb=0.1, elitism=0.8):
    population = [generateRandomItem(cities, costFnc) for i in range(populationNum)]
    for i in range(maxIterations):
        winners = tournamentSelection(population)
        offsprings = []
        w = len(winners)
        while (len(offsprings) < populationNum):
            x = winners[random.randint(0, w-1)]
            y = winners[random.randint(0, w-1)]
            xnew, ynew = crossover(x,y, costFnc, crProb)
            xmut = mutation(xnew, localSearchFnc, costFnc,mtProb)
            ymut = mutation(ynew, localSearchFnc, costFnc, mtProb)
            offsprings.append(xmut)
            offsprings.append(ymut)
        population = combination(population, offsprings, elitism)
    return min(population, key=lambda x: x.cost)   

def generateRandomItem(n, costFnc):
    tour = [i for i in range(n)]
    random.shuffle(tour)
    return GAItem(tour, costFnc(tour))

def tournamentSelection(population):
    winners = []
    n = len(population)
    while (len(winners) < n/2):
        x = population[random.randint(0,n-1)]
        y = population[random.randint(0,n-1)]
        if x.cost < y.cost:
            winners.append(copy.copy(x))
        else:
            winners.append(copy.copy(x))
    return winners

def crossover(x,y, costFnc, crProb):
    if random.random() <= crProb:
        xnew = orderCrossoverOneSide(x.tour,y.tour)
    else:
        xnew = copy.copy(x.tour)
    if random.random() <= crProb:
        ynew = orderCrossoverOneSide(y.tour,x.tour)
    else:
        ynew = copy.copy(y.tour)
    return (GAItem(xnew, costFnc(xnew)), GAItem(ynew, costFnc(ynew)))        

def orderCrossoverOneSide(xTour, yTour):
    x = 0
    y = 0
    while x==y:
        x = random.randint(0,len(xTour)-1)
        y = random.randint(0,len(xTour)-1)
    leftPoint = min(x,y)
    rightPoint = max(x,y)
    tour = [-1]*len(xTour)
    inTour = [False]*len(xTour)
    #fill center
    for i in range(leftPoint, rightPoint+1, 1):
        tour[i] = xTour[i]
        inTour[tour[i]] = True
    #fill the rest
    parentIndex = rightPoint+1 if rightPoint + 1 < len(xTour) else 0
    offspringIndex = parentIndex
    nodesToAdd = len(xTour) - rightPoint + leftPoint - 1 #len - (right - left + 1)
    while nodesToAdd > 0:
        pNode = yTour[parentIndex]
        if inTour[pNode]:
            parentIndex = parentIndex + 1 if parentIndex + 1 < len(xTour) else 0
            continue
        else:
            tour[offspringIndex] = yTour[parentIndex]
            inTour[tour[offspringIndex]] = True
            nodesToAdd -= 1
            parentIndex = parentIndex + 1 if parentIndex + 1 < len(xTour) else 0
            offspringIndex = offspringIndex + 1 if offspringIndex + 1 < len(xTour) else 0
    return tour 

def mutation(x, localSearchFnc, costFnc, mtProb):
    if random.random() <= mtProb:
        xnew = localSearchFnc(x.tour)
    else:
        xnew = copy.copy(x.tour)
    return GAItem(xnew, costFnc(xnew))

def combination(population, offsprings, elitism):
    n = len(population)
    nel = int(n*elitism)
    population.extend(offsprings)
    population.sort(key=lambda x: x.cost)
    total = len(population) - 1
    newPopulation = population[:nel]
    while(len(newPopulation) < n):
        newPopulation.append(population[random.randint(0, total)])
    return newPopulation
