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
    
    def update_function_return_type(self, name, ret_type):
        """
        Updates the return type of an already declared function.
        During the declaration of the function the return type is set to 'any'.
        After the visit of the body, it is possible to update the real return type.
        """
        for scope in reversed(self.symbol_table):
            if name in scope:
                entry = scope[name]
                if isinstance(entry, dict) and entry.get('tag') == 'function':
                    entry['ret_type'] = ret_type
                    return

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
                val = self.lookup(name)
                if val is None:
                    raise Exception(f"Semantic Error: variable '{name}' is not defined.")
                
                if isinstance(val, dict) and val.get('tag') == 'function':  # if val is a dictionary it means it is a function used as variable
                    return 'function'

                return val
            
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
            
            case BinOp(left, '*', right):
                left_type = self.visit(left)
                right_type = self.visit(right)

                if left_type == 'any' or right_type == 'any':
                    return 'any'
                
                if left_type == 'int' and right_type == 'int':
                    return 'int'
                
                if (left_type == 'str' and right_type == 'int') or (left_type == 'int' and right_type == 'str'):
                    return 'str'
                
                raise Exception(f"Semantic Error: type mismatch in multiplication. Cannot multiply {left_type} with {right_type}.")
            
            # '-', '*', '/' are just used for arithmetics operations
            case BinOp(left, op, right) if op in ['-', '/']:
                left_type = self.visit(left)
                right_type = self.visit(right)

                if left_type == 'any' or right_type == 'any':
                    return 'any'

                if left_type == 'str' or right_type == 'str':
                    raise Exception(f"Semantic Error: '{op}' doesn't accept strings.")
                
                return 'int'
            
            case BinOp(left, op, right) if op in ['==', '!=']:
                left_type = self.visit(left)
                right_type = self.visit(right)
                # No type checking needed because we can compare different types and it return False -> 1 == '1' return False.
                return 'bool'   
            
            # '>', '<', '>=', '<=' end in this section
            case BinOp(left, op, right) if op in ['>', '<', '>=', '<=']:
                left_type = self.visit(left)
                right_type = self.visit(right)
                
                if left_type == 'any' or right_type == 'any':
                    return 'bool'
                
                if left_type != right_type:
                    raise Exception(f"Semantic Error: type mismatch in comparison. Cannot compare {left_type} with {right_type}.")
                
                return 'bool'
                
            # 'and', 'or' end in this section
            case BinOp(left, op, right) if op in ['and', 'or']:
                left_type = self.visit(left)
                right_type = self.visit(right)

                if left_type == right_type:
                    return left_type
                
                return 'any'
            
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
                if len(self.symbol_table) <= 1:
                    raise Exception("Semantic Error: 'return' statement outside function")
                
                if value is not None:
                    return self.visit(value)
                return 'any'

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
                func_entry = {
                    'tag': 'function',
                    'params': params,
                    'ret_type': 'any'   # if this is not modified it means that we didn't find any other type
                }
                self.define(name, func_entry)

                self.enter_scope()

                for p in params:
                    self.define(p, 'any')   # because we don't infer input types of params

                inferred_type = 'any'

                try:
                    for stmt in body:
                        stmt_type = self.visit(stmt)

                        if isinstance(stmt, ReturnStat):
                            inferred_type = stmt_type   # we always take the last returned type. We overwrite eventual multiple subsequent returns
                finally:
                    self.exit_scope()

                self.update_function_return_type(name, inferred_type)

            case FunctionCall(name, args):
                func_entry = self.lookup(name)

                if not func_entry:
                    raise Exception(f"Semantic Error: function '{name}' is not defined.")
                
                if not isinstance(func_entry, dict) or func_entry.get('tag') != 'function':
                    raise Exception(f"Semantic Error: '{name}' is not a function")
                
                param_count = len(func_entry['params'])
                arg_count = len(args)

                if param_count != arg_count:
                    raise Exception(f"Semantic Error: Function '{name}' expects {param_count} arguments, but got {arg_count}.")
                
                for arg in args:
                    self.visit(arg)
                
                return func_entry['ret_type']

            case _:
                raise Exception(f"Unknown AST node: '{node}'")


