#gaProcedure
import copy
import random

class GAItem:
    def __init__(self, tour, cost):
        self.tour = tour
        self.cost = cost
    
    def __str__(self):
        return f"c={self.cost:.2f} => {self.tour}"

def gaProcedure(populationNum, maxIterations, costFnc, generateItemFnc, crossoverOneSideFnc, muttationFnc, crProb=0.9, mtProb=0.1, elitism=0.8):
    population = [generateItemFnc(costFnc) for i in range(populationNum)]
    for i in range(maxIterations):
        winners = tournamentSelection(population)
        offsprings = []
        w = len(winners)
        while (len(offsprings) < populationNum):
            x = winners[random.randint(0, w-1)]
            y = winners[random.randint(0, w-1)]
            xnew, ynew = crossover(x,y, costFnc, crProb, crossoverOneSideFnc)
            xmut = muttationFnc(xnew, costFnc,mtProb)
            ymut = muttationFnc(ynew, costFnc, mtProb)
            offsprings.append(xmut)
            offsprings.append(ymut)
        population = combination(population, offsprings, elitism)
    return min(population, key=lambda x: x.cost)    

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

def crossover(x,y, costFnc, crProb, crossoverOneSideFnc):
    if random.random() <= crProb:
        xnew = crossoverOneSideFnc(x,y)
    else:
        xnew = copy.copy(x)
    if random.random() <= crProb:
        ynew = crossoverOneSideFnc(y,x)
    else:
        ynew = copy.copy(y)
    return (xnew, ynew)

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
