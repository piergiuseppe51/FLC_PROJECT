from lexer import lexer
from parser import parser
from parser import (
    Number, String, Boolean, Var, BinOp, UnaryOp, 
    AssignStat, PrintStat, IfStat, ForStat, InputExpr, 
    FunctionDecl, FunctionCall, ExprStat, ReturnStat
)
import textwrap

class CodeGenerator:
    """
    Translates the AST into JavaScript code
    """

    def __init__(self):
        self.indent_level = 0
        # Stack of sets to track declared variables in nested scopes.
        # Index 0 is the global scope
        self.scopes = [set()]

# -------------------Helper Methods------------------

    def get_indent(self):
        """Returns the indentation string based on the current level
        - level 0 will have 0 spaces
        - level 1 will have 4 spaces
        - ...
        - level n will have 4*n spaces
        """
        return "    " * self.indent_level

    def enter_scope(self):
        """Increases indent level and appends a new scope set"""
        self.indent_level += 1
        self.scopes.append(set())

    def exit_scope(self):
        """Decreases indent level and pops the current scope set"""
        self.indent_level -= 1
        self.scopes.pop()

    def declare_var(self, name):
        """Declare a new variable in the current scope"""
        self.scopes[-1].add(name)

    def is_var_declared(self, name):
        """Checks if a variable is already defined starting from the current scope to the global scope.
        - Returns True: if the variable already exists
        - Returns False: if it's a new variable"""
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False
# -------------------------------------------------------------

    def generate(self, node):
        """Generates JavaScript code passing through the AST nodes"""
        match node:
            # ---Statement Lists---
            case list(statements):
                results = []
                for stmt in statements:
                    res = self.generate(stmt)
                    if res:
                        results.append(res)
                return "\n".join(results)

            # ---Primitives---
            case Number(value):
                return str(value)
            
            case String(value):
                # String must have " " 
                return f'"{value}"'
            
            case Boolean(value):
                # Python 'True' -> JS 'true'
                return str(value).lower()

            case Var(name):
                return name
            
            # ---Operations---
            case BinOp(left, op, right):
                js_left = self.generate(left)
                js_right = self.generate(right)
                
                # Map Python operators to JS equivalents
                op_map = {
                    'and': '&&',
                    'or': '||',
                    '==': '===',
                    '!=': '!==',
                    'not': '!'
                }
                js_op = op_map.get(op, op) # Keep the original op if op is not in op_man
                return f"{js_left} {js_op} {js_right}"

            case UnaryOp(op, expr):
                js_expr = self.generate(expr)
                if op == 'not':
                    return f"!{js_expr}"
                return f"{op}{js_expr}"
            
            # ---Statements and Assignments---
            case AssignStat(name, value):
                js_val = self.generate(value)
                indent = self.get_indent()
                
                # If variable exists reassign it. If it's new declare it with 'let'
                if self.is_var_declared(name):
                    return f"{indent}{name} = {js_val};"
                else:
                    self.declare_var(name)
                    return f"{indent}let {name} = {js_val};"

            case PrintStat(value):
                indent = self.get_indent()
                js_val = self.generate(value)
                return f'{indent}console.log({js_val});'

            case ReturnStat(value):
                indent = self.get_indent()
                js_val = self.generate(value)
                return f'{indent}return {js_val};'
            
            case ExprStat(expr):
                indent = self.get_indent()
                js_expr = self.generate(expr)
                return f'{indent}{js_expr};'

            case InputExpr(prompt):
                return f'prompt("{prompt}")'

            # ---Control Flow---
            case IfStat(condition, true_block, false_block):
                indent = self.get_indent()
                js_cond = self.generate(condition)
                
                # IF block
                result = f"{indent}if ({js_cond}) {{\n"
                
                self.enter_scope()
                result += self.generate(true_block) + "\n"
                self.exit_scope()
                
                result += f"{indent}}}"

                # ELSE block (handles ELIF recursively nesting other IFStats)
                if false_block:
                    result += " else {\n"
                    self.enter_scope()
                    result += self.generate(false_block) + "\n"
                    self.exit_scope()
                    result += f"{indent}}}"
                
                return result

            case ForStat(iterator, start, end, body):
                # Python: for i in range(start, end)
                # JS: for (let i = start; i < end; i++)
                
                indent = self.get_indent()
                js_start = self.generate(start)
                js_end = self.generate(end)
                
                self.enter_scope()
                self.declare_var(iterator)
                
                header = f"for (let {iterator} = {js_start}; {iterator} < {js_end}; {iterator}++)"
                
                result = f"{indent}{header} {{\n"
                result += self.generate(body) + "\n"
                
                self.exit_scope()
                result += f"{indent}}}"
                return result

            case FunctionDecl(name, params, body):
                indent = self.get_indent()
                params_str = ", ".join(params)
                
                self.declare_var(name) # Function name is visible in current scope
                
                result = f"{indent}function {name}({params_str}) {{\n"
                
                self.enter_scope()
                # Parameters are local variables inside the function
                for p in params:
                    self.declare_var(p)
                    
                result += self.generate(body) + "\n"
                self.exit_scope()
                
                result += f"{indent}}}"
                return result

            # ---Functions---
            case FunctionCall(name, args):
                js_args = ", ".join([self.generate(arg) for arg in args])
                return f"{name}({js_args})"

            case None:
                return ""
            
            case _:
                raise Exception(f"Codegen Error: Unknown node '{node}'")

# ---TEST---
if __name__ == '__main__':
    
    # Codice Python di input 
    test_code = textwrap.dedent("""
    groupSize = 2
    groupMember1 = "Andrea"
    workingOnTranspiler = True
    componentsToDevelop = 4

    def encourage_team(member, status):
        if member == "Andrea" and not status:
            print("Wake up!")
            return 0
        elif status == True:
            print("Great work!")
            return 1
        else:
            return -1

    if workingOnTranspiler:
        print("Starting coding session...")
        
        if groupSize == 2:
            print("Team complete.")
            
            for i in range(componentsToDevelop):
                remaining = 4 - i
                print(remaining)
                
        print("Session ended.")
    """)

    print(f"--- INPUT PYTHON ---\n{test_code}\n")

    # 1. Lexing & Parsing
    lexer.lineno = 1
    ast = parser.parse(test_code, lexer=lexer)
    
    if ast:
        # 2. Codegen
        print("--- GENERATING JAVASCRIPT ---")
        codegen = CodeGenerator()
        js_code = codegen.generate(ast)
        print(js_code)
        print("-----------------------------")
    else:
        print("Parsing failed.")