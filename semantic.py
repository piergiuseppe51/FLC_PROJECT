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
        """Appends a new scope dictionary { } to the stack"""
        self.symbol_table.append({})
    
    def exit_scope(self):
        """Removes the current scope dictionary { } from the stack"""
        self.symbol_table.pop()

    def define(self, name, type_):
        """Define a new variable or function to the current scope"""
        self.symbol_table[-1][name] = type_

    def lookup(self, name):
        """
        Searches for a variable starting from the current scope in reverse to the global scope [0].
        - Returns the type if the variable is found, otherwise returns None
        """
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        return None

# -----------------------------------------

    def visit(self, node):
        """
        Navigates through the AST nodes generate by the parser.
        - Returns the type for the expressions: Number, String, Boolean, InputExpr, AssignStat, Var, BinOp, UnaryOp
        - Returns None for the statements: PrintStat, ExprStat, ReturnStat, IfStat, ForStat, FunctionDecl
        """
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

                if left_type == 'any' or right_type == 'any':
                    return 'any'

                if (left_type == 'str' and right_type == 'int') or \
                    (left_type == 'int' and right_type == 'str'):
                    raise Exception(f"Semantic Error: type mismatch in sum. Cannot add {left_type} with {right_type}.")
                return left_type
            
            # '-', '*', '/' are just used for arithmetics operations
            case BinOp(left, op, right) if op in ['-', '*', '/']:
                left_type = self.visit(left)
                right_type = self.visit(right)

                if left_type == 'str' or right_type == 'str':
                    raise Exception(f"Semantic Error: '{op}' doesn't accept strings.")
                return 'int'
            
            # '>', '<', '>=', '<=', '==', '!=' end in this section
            case BinOp(left, op, right) if op in ['>', '<', '>=', '<=', '==', '!=']:
                left_type = self.visit(left)
                right_type = self.visit(right)
                
                if left_type == 'any' or right_type == 'any':
                    return 'bool'
                
                if left_type != right_type:
                    raise Exception(f"Semantic Error: type mismatch in comparison. Cannot compare {left_type} with {right_type}.")
                
                if op in ['>', '<', '>=', '<='] and left_type not in ['int', 'str']:
                    raise Exception(f"Semantic Error: Operator {op} not supported for type {left_type}")
                
                return 'bool'
                
            # 'and', 'or' end in this section
            case BinOp(left, op, right) if op in ['and', 'or']:
                left_type = self.visit(left)
                right_type = self.visit(right)
                
                if left_type != 'bool' and left_type != 'any':
                    raise Exception(f"Semantic Error: left side of '{op}' must be boolean, got {left_type}")
                if right_type != 'bool' and right_type != 'any':
                    raise Exception(f"Semantic Error: right side of '{op}' must be boolean, got {right_type}")
                
                return 'bool'
            
            # 'not' for boolean values
            case UnaryOp('not', expr):
                self.visit(expr)
                return 'bool'
            
            # '-' for negative numbers
            case UnaryOp('-', expr):
                expr_type = self.visit(expr)
                if expr_type == 'str':
                    raise Exception("Semantic Error: cannot use '-' on a string.")
                return 'int'
            
            case PrintStat(value):
                self.visit(value)

            case ExprStat(expr):
                self.visit(expr)
            
            case ReturnStat(value):
                self.visit(value)

            # IF statement without ELSE
            case IfStat(condition, true_block, None):
                self.visit(condition)
                self.visit(true_block)

            # IF statement with ELSE
            case IfStat(condition, true_block, false_block):
                self.visit(condition)
                self.visit(true_block)
                self.visit(false_block)

            case ForStat(iterator, start, end, body):
                self.define(iterator, 'int')

                start_type = self.visit(start)
                end_type = self.visit(end)

                if start_type not in ['int', 'any'] or end_type not in ['int', 'any']:
                    raise Exception("Semantic Error: FOR loop requires integers.")
                
                self.visit(body)

            case FunctionDecl(name, params, body):
                self.define(name, 'function')
                self.enter_scope()    

                for p in params:
                    self.define(p, 'any')
                try:
                    self.visit(body)
                finally:
                    self.exit_scope()

            case FunctionCall(name, args):
                if not self.lookup(name):
                    raise Exception(f"Semantic Error: '{name}' function is not defined")
                for arg in args:
                    self.visit(arg)
                return 'any'

            case _:
                raise Exception(f"Unknown AST node: '{node}'")


