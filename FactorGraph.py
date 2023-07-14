#!/usr/bin/env python3

from DimacsFile import DimacsFile
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

class FactorGraph(nx.Graph):    
    def __init__(self, nVars, clauses, fEdge=None):
        # clauses contains 1-based variables; + or -; we will convert them to 0-based;
        # we will set the property "J" for all edges: +1 for negative literals or -1 for positive literals;
        # the function fEdge(edge, i, a, True|False) can set additional edge properties; indexes passed will be 0-based
        super().__init__()

        self.N = nVars
        self.C = len(clauses)
        self.iassignment = np.zeros(self.N)  # -1 = False; 0 = unassigned; +1 = True

        self.add_nodes_from(np.arange(self.N + self.C)) # the first N vertices are for vars, the last C are for clauses

        for a in range(self.C): # a = clause index
            c = clauses[a]
            for literal in c:
                i = abs(literal)-1
                J = -1
                if literal<0:
                    J = +1
                self.add_edge(i,self.N+a)
                self[i][self.N+a]['J'] = J
                if fEdge is not None:
                    fEdge(self[i][self.N+a], i, a, literal>0)

    def numberOfVars(self):
        return self.N

    def numberOfClauses(self):
        return self.C

    def decimate(self):
        # removes nodes correspodning to assigned variables i (links to  will be deleted automatically by nx)
        # removes also the clauses satisfied by the assigned variables
        for i in range(self.N):
            if self.iassignment[i] == 0:
                continue # node not assigned yet
            if i not in self.nodes():
                continue # already removed node


            l = []
            for a in self.neighbors(i):
                if self[i][a]['J'] * self.iassignment[i] == -1:
                    l.append(a)
            for a in l:
                self.remove_node(a)
            self.remove_node(i)

    def assign(self, i, value, callDecimate=True): # 0-based index i; value is True or False
        self.iassignment[i] = +1 if value else -1
        if callDecimate:
            self.decimate()

    def allAssigned(self):
        return not np.any(self.iassignment == 0)
    
    def assignment(self):
        return [ True if x==+1 else False for x in self.iassignment ]

    def varNodes(self):
        return set( i for i in range(self.N) if i in self.nodes())
    
    def clauseNodes(self):
        return set( a for a in range(self.N, self.N+self.C) if a in self.nodes())
        
    def plot(self, edgeAttrName=None, maximize=False, nodeAttrName=None):
        if maximize:
            plt.figure(figsize=(18,10))
            
        if not hasattr(self, 'layout'):
            self.layout=nx.spring_layout(self)
            
        vars = self.varNodes()
        clauses = self.clauseNodes()
            
        nx.draw_networkx_nodes(self, self.layout, nodelist=vars) # nodelist=... only specific nodes
        nx.draw_networkx_nodes(self, self.layout, node_shape='s', nodelist=clauses) # nodelist=... only specific nodes

        nodeLabels = {}
        for i in vars:
            nodeLabels[i] = str(i+1)
            if nodeAttrName is not None:
                nodeLabels[i] += ":"+str(self.nodes[i][nodeAttrName+'+'])+"/"+str(self.nodes[i][nodeAttrName+'-']) # gamma+ and gamma-
        for a in clauses:
            nodeLabels[a] = "C"+str(a-self.N+1)
        nx.draw_networkx_labels(self, self.layout, labels=nodeLabels)

        for (i,a) in self.edges():
            if self[i][a]['J']==+1:
                nx.draw_networkx_edges(self, self.layout, style='dashed', edgelist=[(i,a)])
            else:
                nx.draw_networkx_edges(self, self.layout, style='solid', edgelist=[(i,a)])                
            if edgeAttrName is not None and edgeAttrName in self[i][a]:
                nx.draw_networkx_edge_labels(self, self.layout, edge_labels={ (i,a): self[i][a][edgeAttrName]})
                
        plt.draw()
        plt.show()

if __name__ == "__main__": # test
    df = DimacsFile("tree.cnf")
    df.load()
    FactorGraph(df.numberOfVars(), df.clauses()).plot()


