import os
import sys
import math
import copy
import random
import matplotlib.pyplot as plt

def loadSPDfromFile(filePath):
    data = []
    with open(filePath, newline='') as dataFile:
        capacity = int(next(dataFile)) 
        depot = next(dataFile).split()
        data.append([float(depot[0]), float(depot[1]), 0, 0])
        for line in dataFile:
            r = line.split()
            data.append([float(r[0]), float(r[1]), float(r[2]), float(r[3])])
    return capacity, SelectivePickupDelivery(data)

class RouteNode:
    def __init__(self, id, delivery, pickup):
        self.id = id
        self.delivery = delivery
        self.pickup = pickup

class SelectivePickupDelivery:
    def __init__(self,data):
        self.coordinates = [(d[0],d[1]) for d in data]
        self.demand = [(d[2],d[3]) for d in data]
    
    def distance(self, x, y):
        """
            x,y valid index
        """
        xn = self.coordinates[x]
        yn = self.coordinates[y]
        return math.sqrt(math.pow(xn[0]-yn[0],2) + math.pow(xn[1]-yn[1],2))

    def getRouteTravelCost(self, tour):
        cost = 0
        for i in range(len(tour)):
            next = i+1 if i+1 < len(tour) else 0
            cost += self.distance(tour[i].id, tour[next].id)
        return cost

    def getSolutionTravelCost(self,routeSet):
        return sum([self.getRouteTravelCost(r) for r in routeSet])
    
    def getTotalPickup(self, tour):
        return sum([n.pickup for n in tour])

    def getTotalDelivery(self, tour):
        return sum([n.delivery for n in tour])

    def getRouteCost(self, tour, capacity, penalization):
        travelCost = self.getRouteTravelCost(tour)
        totalDelivery = self.getTotalDelivery(tour)
        overload = max(0, totalDelivery-capacity)
        return travelCost + penalization*overload

    def getSolutionCost(self, routeSet, capacity, penalization):
        return sum([self.getRouteCost(r, capacity, penalization) for r in routeSet])


    def setPickupDemand(self, tour, capacity):
        currentLoad = self.getTotalDelivery(tour)
        for n in tour:
            currentLoad -= n.delivery
            n.pickup = min(self.demand[n.id][1], capacity - currentLoad)
            currentLoad += n.pickup
        return tour


def main():
    capacity, prob = loadSPDfromFile("spd1.txt")
    print(capacity)
    print(prob.demand)
    
if __name__ == "__main__":
    main()
        
    




