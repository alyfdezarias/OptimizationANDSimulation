#assignment problem

import os
import re
import sys
import copy
import argparse
from scipy.optimize import linear_sum_assignment

def loadProblemFromFile(filePath):
    cost = []
    with open(filePath, newline='') as dataFile:
        nline = next(dataFile)
        n = int(nline.replace("n=", ""))
        for s in range(n):
            line = next(dataFile)
            data = line.split()
            row = [int(i) for i in data]
            cost.append(row)
        return cost

#app
def create_parser():
    parser = argparse.ArgumentParser(prog = "assignment")
    parser.add_argument("-t", "--testFile", type = str, default = "assigndata.dat")
    return parser

def printOptimalSolution(sol, prob):
    col_ind = sol[1]
    print("optimal solution")
    for i in range(len(col_ind)):
        print(f"task {i} to machine {col_ind[i]}")
    cost = sum([prob[i][col_ind[i]] for i in range(len(col_ind))])
    print(f"cost={cost}")

def main():
    parser = create_parser()
    args = parser.parse_args()

    prob = loadProblemFromFile(args.testFile)
    row_ind, col_ind = linear_sum_assignment(prob)
    print(f"optimal solution")
    for i in range(len(col_ind)):
        print(f"task {i} to machine {col_ind[i]}")
    cost = sum([prob[i][col_ind[i]] for i in range(len(col_ind))])
    print(f"cost={cost}")


if __name__ == "__main__":
    main()