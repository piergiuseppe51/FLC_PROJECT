from parser import (
    Number, String, Boolean, Var, BinOp, UnaryOp, 
    AssignStat, PrintStat, IfStat, ForStat, InputExpr, 
    FunctionDecl, FunctionCall, ExprStat, ReturnStat
)

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = [{}]

# --------------Helper methods-------------
    def enter_scope(self):
        self.symbol_table.append({})
    
    def exit_scope(self):
        self.symbol_table.pop()

    def define(self, name, type_):
        self.symbol_table[-1][name] = type_

    def lookup(self, name):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        return None

# -----------------------------------------

    def visit(self, node):
        match node:

            case list(statements):
                for stmt in statements:
                    self.visit(stmt)
                return
            
            case Number(_):  return 'int'
            case String(_):  return 'str'
            case Boolean(_): return 'bool'
            case InputExpr(_): return 'str'

            case AssignStat(name, value):
                value_type = self.visit(value)
                self.define(name, value_type)
                return value_type
            
            case Var(name):
                var_type = self.lookup(name)
                if var_type is None:
                    raise Exception(f"Semantic Error: variable '{name}' is not defined.")
                return var_type
            
            # '+' can handle arithmetic sums and string concatenation
            case BinOp(left, '+', right):
                left_type = self.visit(left)
                right_type = self.visit(right)

                if (left_type == 'str' and right_type == 'int') or \
                    (left_type == 'int' and right_type == 'str'):
                    raise Exception(f"Type mismatch: Cannot add {left_type} with {right_type}.")
                return left_type
            
            # '-', '*', '/' are just used for arithmetics operations
            case BinOp(left, op, right) if op in ['-', '*', '/']:
                left_type = self.visit(left)
                right_type = self.visit(right)

                if left_type == 'str' or right_type == 'str':
                    raise Exception(f"Semantic Error: '{op}' doesn't accept strings.")
                return 'int'
            
            # '>', '<', '==', 'and', 'or' end in this section
            case BinOp(left, op, right):
                self.visit(left)
                self.visit(right)
                return 'bool'
            


