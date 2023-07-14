#!/usr/bin/env python3

class DimacsFile:
    def __init__(self, fname):
        self.fname = fname

    def load(self):
        f = open(self.fname, 'r')
        lines = f.readlines()
        f.close()

        self.iclauses = []
        self.nVars=0
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            i = line.find("p cnf")
            if i>=0:
                line = line[len("p cnf"):].strip()
                i = line.find(" ")
                line = line[:i]
                self.nVars=int(line)
                continue
            if line[0].isalpha():
                continue

            clause = []
            for s in line.split():
                i = int(s)
                if i == 0:
                    break  # end of clause
                clause.append(i)
            self.iclauses.append(clause)

    def numberOfVars(self):
        return self.nVars

    def numberOfClauses(self):
        return len(self.iclauses)

    def clauses(self):
        return self.iclauses

if __name__ == "__main__": # test
    df = DimacsFile("gt.cnf")
    df.load()
    print(df.numberOfVars(), df.numberOfClauses(), df.clauses())
