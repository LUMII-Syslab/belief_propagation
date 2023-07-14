#!/usr/bin/env python3

import unittest
from DimacsFile import DimacsFile
from bp import BeliefPropagation
#from bpV import BeliefPropagation
from VariableAssignment import VariableAssignment


def test_cnf(file_name):
        print("fileName="+file_name)
        df = DimacsFile(file_name)
        df.load()

        bp = BeliefPropagation(df.numberOfVars(), df.clauses(), verbose=False)
        bp.run()
        x = bp.solution()
        print(x)
        assignment = VariableAssignment(df.numberOfVars(), df.clauses())
        assignment.assign_all(x)
        df.clauses()
        return assignment.satisfiable()

class MyTestCase(unittest.TestCase):

    def test_tree(self):
        self.assertTrue(test_cnf("tests/tree.cnf"), "tree from tree.cnf must be satisfiable")

    def test_quinn(self):
        self.assertTrue(test_cnf("tests/quinn.cnf"), "factorization problem from quinn.cnf must be satisfiable")


if __name__ == '__main__':
    unittest.main()
