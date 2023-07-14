
class VariableAssignment:
    def __init__(self, n_vars, clauses):
        self.x = False * n_vars
        self.clauses = clauses

    def assign(self, i, value):
        # i must be zero-based
        self.x[i] = value

    def assign_all(self, x):
        self.x = x

    def satisfiable(self):
        for a in range(len(self.clauses)):  # a = clause index
            c = self.clauses[a]
            is_clause_satisfied = False
            for literal in c:
                i = abs(literal) - 1  # zero-based
                if (literal > 0) == self.x[i]:
                    is_clause_satisfied = True
                    break  # the clause is satisfied by x[i], no need to check other vars
            if not is_clause_satisfied:
                return False  # clause c cannot be satisfied
        return True
