#!/usr/bin/env python3

import numpy as np
import networkx as nx
import math

from DimacsFile import DimacsFile
from SomePropagationV import SomePropagationV


class BeliefPropagation(SomePropagationV):

    def __init__(self, nVars, clauses, max_iter=10, eps=0.05, verbose=False):
        super().__init__(nVars, clauses, max_iter, eps, verbose, 'delta', 'gamma')
        self.generateRandomVariableStates()

    def gammaStr(self, i, a):
        if self.factorGraph[i][a]['J'] == -1:
            return 'gamma+'
        else:
            return 'gamma-'

    def generateRandomVariableStates(self):
        for i in range(self.factorGraph.N):
            if i in self.factorGraph.nodes():
                self.factorGraph.nodes[i]['gamma+'] = np.random.rand(
                    1)[0]  # prob. that var i violates clauses with positive literals x_i
                self.factorGraph.nodes[i]['gamma-'] =self.factorGraph.nodes[i]['gamma-'] = np.random.rand(
                    1)[0]  # prob. that var i violates clauses negative literals ~x_i

    def currentState(self):
        gammas = list(nx.get_node_attributes(self.factorGraph, 'gamma+').values()) + list(nx.get_node_attributes(self.factorGraph, 'gamma-').values())
        return np.array(gammas, dtype="object")

    def markState(self):
        self.oldState = self.currentState()

    def converged(self):
        return np.all(np.abs(self.oldState - self.currentState()) < self.eps)

    def updateVariableState(self, i):
        result = 1.0
        for a in self.factorGraph.neighbors(i):

            p = 1.0
            for j in self.factorGraph.neighbors(a):
                if j == i:
                    continue
                p *= self.factorGraph.nodes[j][self.gammaStr(j, a)]

            # p = probability that a needs i (delta_a->i from the paper)
            self.factorGraph[i][a]['delta'] = p

        # recompute new gamma+ and gamma- using deltas:
        p1 = 1.0
        p2 = 1.0
        for b in self.factorGraph.neighbors(i):
            if self.factorGraph[i][b]['J'] == -1:
                p1 *= (1 - self.factorGraph[i][b]['delta'])
            else:
                p2 *= (1 - self.factorGraph[i][b]['delta'])

        if abs(p1)<1e-50 and abs(p2)<1e-50:
          self.factorGraph.nodes[i]['gamma+'] = 0.5
          self.factorGraph.nodes[i]['gamma-'] = 0.5
        else:
          self.factorGraph.nodes[i]['gamma+'] = p1 / (p1 + p2)
          self.factorGraph.nodes[i]['gamma-'] = p2 / (p1 + p2)

    def prepareAssignment(self):
        self.truthProb = [np.nan] * self.factorGraph.N
        for i in range(self.factorGraph.N):
            if i in self.factorGraph.nodes():
                Ppos = self.factorGraph.nodes[i]['gamma+']
                Pneg = self.factorGraph.nodes[i]['gamma-']

                if Ppos + Pneg < 0.0001:  # == 0
                    self.truthProb[i] = 0.5
                else:
                    self.truthProb[i] = Pneg / (Pneg + Ppos)

        self.generateRandomVariableStates()  # for the next step

    def unsatisfiable(self):
        return np.all(self.truthProb == np.nan)

    def localAssignment(self):
        if self.verbose:
            print("probabilities of True: ", self.truthProb)
        i = np.nanargmax(self.truthProb)
        if self.truthProb[i] > 0.5:
            if self.verbose:
                print("assigning " + str(i) + " to True")
            return [(i, True)]
        i = np.nanargmin(self.truthProb)
        if self.verbose:
            print("assigning " + str(i) + " to False")
        return [(i, False)]


# main BP
if __name__ == '__main__':
  df = DimacsFile("tests/quinn.cnf")
  df.load()

  bp = BeliefPropagation(df.numberOfVars(), df.clauses(), verbose=True)
  bp.run()
  print(bp.solution())
