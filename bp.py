#!/usr/bin/env python3

import numpy as np
import networkx as nx

from DimacsFile import DimacsFile
from SomePropagation import SomePropagation


class BeliefPropagation(SomePropagation):

    def __init__(self, nVars, clauses, max_iter=10, eps=0.2, verbose=False):
        super().__init__(nVars, clauses, max_iter, eps, verbose, 'delta')
        self.generateRandomDeltas()

    def generateRandomDeltas(self):
        for (i,a) in self.factorGraph.edges():
            self.factorGraph[i][a]['delta'] = np.random.rand(1)[0] # in the paper it is delta_a->i, but our indices are [i][a]['delta']

    def currentState(self):
        return np.array(list(nx.get_edge_attributes(self.factorGraph, 'delta').values()), dtype="object")

    def markState(self):
        self.oldState = self.currentState()

    def converged(self):
        return np.all(np.abs(self.oldState - self.currentState()) < self.eps)

    def update(self, i, a):
        result = 1.0
        for j in self.factorGraph.neighbors(a):
            if j==i:
                continue
            Pu = 1.0
            Ps = 1.0
            J = self.factorGraph[j][a]['J']
            for b in self.factorGraph.neighbors(j):
                if a==b:
                    continue
                if self.factorGraph[j][b]['J']==J: # b with the same sign
                    Pu *= (1-self.factorGraph[j][b]['delta'])
                else:
                    Ps *= (1-self.factorGraph[j][b]['delta'])
            gamma = Pu/(Pu+Ps)
            result *= gamma
        self.factorGraph[i][a]['delta'] = result

    def prepareAssignment(self):
        self.truthProb = [np.nan] * self.factorGraph.N
        for i in range(self.factorGraph.N):
            if i in self.factorGraph.nodes():
                Ppos = 1.0
                Pneg = 1.0
                for a in self.factorGraph.neighbors(i):
                    if self.factorGraph[i][a]['J'] == -1: # -1 means positive literal; +1 means negative literal
                        Ppos *= (1-self.factorGraph[i][a]['delta'])
                    else:
                        Pneg *= (1-self.factorGraph[i][a]['delta'])

                if Ppos + Pneg < 0.0001: # == 0
                    self.truthProb[i] = 0.5
                else:
                    self.truthProb[i] = Pneg/(Pneg+Ppos)

        self.generateRandomDeltas() # for the next step

    def unsatisfiable(self):
        return np.all(self.truthProb == np.nan)

    def localAssignment(self):
        if self.verbose:
            print("probabilities of True: ",self.truthProb)
        i = np.nanargmax(self.truthProb)
        if self.truthProb[i]>0.5:
            if self.verbose:
                print("assigning "+str(i)+" to True")
            return [(i, True)]
        i = np.nanargmin(self.truthProb)
        if self.verbose:
            print("assigning "+str(i)+" to False")
        return [(i, False)]

# main BP
if __name__ == '__main__':
  df = DimacsFile("tests/quinn.cnf")
  df.load()

  bp = BeliefPropagation(df.numberOfVars(), df.clauses(), verbose=True)
  bp.run()
  print(bp.solution())
