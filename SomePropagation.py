#!/usr/bin/env python3

import abc
import numpy as np
import networkx as nx
from random import shuffle
import matplotlib.pyplot as plt

from FactorGraph import FactorGraph
from DimacsFile import DimacsFile


class SomePropagation(metaclass=abc.ABCMeta):
    def __init__(self, nVars, clauses, max_iter, eps, verbose, edgeAttrName = None):
        self.factorGraph = FactorGraph(nVars, clauses)
        self.max_iter = max_iter
        self.eps = eps
        self.verbose = verbose
        self.edgeAttrName = edgeAttrName

    @abc.abstractmethod
    def markState(self):
        pass

    @abc.abstractmethod
    def update(self, i, a):
        pass

    @abc.abstractmethod
    def converged(self):
        pass

    @abc.abstractmethod
    def prepareAssignment(self):
        pass

    @abc.abstractmethod
    def unsatisfiable(self):
        pass

    @abc.abstractmethod
    def localAssignment(self):
        pass

    def print(self):
        for i in range(self.factorGraph.N):
            if i in self.factorGraph.nodes():
                print("var "+str(i+1)+": ", end='')
                if self.edgeAttrName is not None:
                    for a in self.factorGraph.neighbors(i):
                        print("->"+chr(97+a-self.factorGraph.N)+" "+str(self.factorGraph[i][a][self.edgeAttrName])+"  ", end = '')                          
                    print()
        
    def runStep(self):
        if self.verbose:
            print("runStep")
        self.convergeStatus = False
        for t in range(self.max_iter):
            if self.verbose:
                print("  step iteration "+str(t))
                self.print()
                self.factorGraph.plot(self.edgeAttrName, maximize=True)
            L = list(self.factorGraph.edges())
            shuffle(L)

            self.markState()
            for (i,a) in L:
                self.update(i,a)

            if self.converged():
                self.convergeStatus = True
                return # all OK
            
        if self.verbose:
            print("not converged")


    def run(self):
        while not self.factorGraph.allAssigned():
            self.runStep()
            if not self.convergeStatus:
                break
            self.prepareAssignment()
            if self.unsatisfiable():
                if self.verbose:
                    print("unsatisfiable")
                break

            for (i,value) in self.localAssignment():
                if self.verbose:
                    print("forward assignment for var "+str(i)+" to ",value)
                self.factorGraph.assign(i, value, False) # do not decimate for now
            self.factorGraph.decimate()
            
    def solution(self):
        return self.factorGraph.assignment()

