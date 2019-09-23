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
        self.__getDistanceMatrix()
    
    def __getDistanceMatrix(self):
        self.distanceArray=[]
        for x in self.coordinates:
            dist = []
            for y in self.coordinates:
                dist.append(math.sqrt(math.pow(x[0]-y[0],2) + math.pow(x[1]-y[1],2)))
            self.distanceArray.append(dist)

    def distance(self, x, y):
        """
            x,y valid index
        """
        xn = self.coordinates[x]
        yn = self.coordinates[y]
        return math.sqrt(math.pow(xn[0]-yn[0],2) + math.pow(xn[1]-yn[1],2))

    def getRouteTravelCost(self, tour):
        cost = 0
        prev = 0
        for i in range(len(tour)):
            cost += self.distanceArray[prev][tour[i].id]
            prev = tour[i]
        cost += self.distanceArray[prev][0]
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

    def greedySol_unlimitvehicles(self, capacity):
        routeSet = []
        pass



def main():
    capacity, prob = loadSPDfromFile("spd1.txt")
    print(prob.distanceArray)
    
if __name__ == "__main__":
    main()
        
    




