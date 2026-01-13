from parser import (
    Number, String, Boolean, Var, BinOp, UnaryOp, 
    AssignStat, PrintStat, IfStat, ForStat, InputExpr, 
    FunctionDecl, FunctionCall, ExprStat, ReturnStat
)

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = [{}]
        self.call_stack = set()

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
                last_type = None
                for stmt in statements:
                    res = self.visit(stmt)

                    if res is not None:
                        last_type = res
                return last_type
            
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

            # IF statement
            case IfStat(condition, true_block, false_block):
                self.visit(condition)
                true_type = self.visit(true_block)
                false_type = self.visit(false_block) if false_block else None

                if true_type and false_type and (true_type == false_type):
                    return true_type
                
                if true_type: return true_type
                if false_type: return false_type
                return None

            case ForStat(iterator, start, end, body):
                self.define(iterator, 'int')

                start_type = self.visit(start)
                end_type = self.visit(end)

                if start_type not in ['int', 'any'] or end_type not in ['int', 'any']:
                    raise Exception("Semantic Error: FOR loop requires integers.")
                
                return self.visit(body)
                

            case FunctionDecl(name, params, body):
                func_entry = {
                    'tag': 'function',
                    'params': params,
                    'body': body,
                    'cache': {}
                }
                self.define(name, func_entry)

            case FunctionCall(name, args):
                func_entry = self.lookup(name)

                if not func_entry:
                    raise Exception(f"Semantic Error: function '{name}' is not defined.")
                
                if not isinstance(func_entry, dict) or func_entry.get('tag') != 'function':
                    raise Exception(f"Semantic Error: '{name}' is not a function")
                
                params = func_entry['params']
                if len(params) != len(args):
                    raise Exception(f"Arg count mismatch for '{name}'. Expected {len(params)}, got {len(args)}.")
                
                arg_types = tuple([self.visit(arg) for arg in args])

                if arg_types in func_entry['cache']:
                    return func_entry['cache'][arg_types]
                
                call_signature = (name, arg_types)
                if call_signature in self.call_stack:
                    return 'any'
                
                self.call_stack.add(call_signature)
                self.enter_scope()

                try:
                    for param_name, arg_type in zip(params, arg_types):
                        self.define(param_name, arg_type)
                    
                    body_node = func_entry['body']

                    inferred_ret_type = self.visit(body_node)

                    if inferred_ret_type is None:
                        inferred_ret_type = 'any'
                    
                    func_entry['cache'][arg_types] = inferred_ret_type
                    return inferred_ret_type
                
                finally:
                    self.exit_scope()
                    self.call_stack.remove(call_signature)

            case _:
                raise Exception(f"Unknown AST node: '{node}'")

