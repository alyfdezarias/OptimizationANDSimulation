import os
import sys
import random

def generatePickupDeliveryProblemFromCVRP(inFile, outFile):
    capacity, depot, data = loadDataFromCVPFile(inFile)
    with open(outFile, "w", newline='') as dataFile:
        dataFile.write(f"{capacity}\n")
        dataFile.write(f"{float(depot[0])} {float(depot[1])}\n")
        for r in data:
            demand = r[2]
            pickup = random.randint(int(demand*0.5), int(demand*1.5))
            dataFile.write(f"{r[0]} {r[1]} {demand} {pickup}\n")

def loadDataFromCVPFile(filename):
    data = []
    with open(filename, newline='') as dataFile:
        header = next(dataFile).split() #header line=> number of customers, capacity, maximum route time, drop time
        depot = next(dataFile).split() #depot line=> x, y 
        for line in dataFile:
            r = line.split() #x,y,demand
            data.append([float(r[0]), float(r[1]), float(r[2])])
    return header[1], depot, data

def main():
    generatePickupDeliveryProblemFromCVRP("vrpnc1.txt", "spd1.txt")

    
if __name__ == "__main__":
    main()


    