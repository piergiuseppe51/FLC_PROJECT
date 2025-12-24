from lexer import lexer
from parser import parser
from parser import (
    Number, String, Boolean, Var, BinOp, UnaryOp, 
    AssignStat, PrintStat, IfStat, ForStat, InputExpr, 
    FunctionDecl, FunctionCall, ExprStat, ReturnStat
)
import textwrap

class CodeGenerator:
    def __init__(self):
        self.indent_level = 0
        # Stack di set per tracciare le variabili dichiarate in ogni scope.
        # Iniziamo con lo scope globale.
        self.scopes = [set()]

    def get_indent(self):
        return "    " * self.indent_level

    def enter_scope(self):
        self.indent_level += 1
        self.scopes.append(set())

    def exit_scope(self):
        self.indent_level -= 1
        self.scopes.pop()

    def declare_var(self, name):
        """Registra una variabile nello scope corrente."""
        self.scopes[-1].add(name)

    def is_var_declared(self, name):
        """Controlla se la variabile esiste in qualsiasi scope attivo (locale o genitore)."""
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False

    def generate(self, node):
        match node:
            # --- Gestione Liste di Statement (Programma o Blocchi) ---
            case list(statements):
                results = []
                for stmt in statements:
                    res = self.generate(stmt)
                    if res:
                        results.append(res)
                return "\n".join(results)

            # --- Valori Primitivi ---
            case Number(value):
                return str(value)
            
            case String(value):
                # Assicura che le stringhe abbiano doppi apici in JS
                return f'"{value}"'
            
            case Boolean(value):
                # Python 'True' -> JS 'true'
                return str(value).lower()

            case Var(name):
                return name

            # --- Operazioni ---
            case BinOp(left, op, right):
                js_left = self.generate(left)
                js_right = self.generate(right)
                
                # Mappatura operatori Python -> JS
                op_map = {
                    'and': '&&',
                    'or': '||',
                    '==': '===', # Strict equality
                    '!=': '!==',
                    'not': '!'
                }
                js_op = op_map.get(op, op) # Se non è nella map, usa l'originale (+, -, *, /)
                return f"{js_left} {js_op} {js_right}"

            case UnaryOp(op, expr):
                js_expr = self.generate(expr)
                if op == 'not':
                    return f"!{js_expr}"
                return f"{op}{js_expr}"

            # --- Statement ---
            case AssignStat(name, value):
                js_val = self.generate(value)
                indent = self.get_indent()
                
                # Se la variabile esiste già, è una riassegnazione.
                # Se è nuova, usiamo 'let'.
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
                # 'input' in Python -> 'prompt' in Browser JS
                # Nota: Node.js non ha prompt nativo sincrono, ma per JS generico si usa prompt()
                return f'prompt("{prompt}")'

            # --- Strutture di Controllo ---
            case IfStat(condition, true_block, false_block):
                indent = self.get_indent()
                js_cond = self.generate(condition)
                
                # Inizio blocco IF
                result = f"{indent}if ({js_cond}) {{\n"
                
                self.enter_scope()
                result += self.generate(true_block) + "\n"
                self.exit_scope()
                
                result += f"{indent}}}"

                # Gestione ELSE / ELIF
                if false_block:
                    # In Python, elif è gestito dal parser come un IfStat annidato nel false_block
                    # Qui generiamo un semplice "else { ... }"
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
                
                # Iniziamo il loop e dichiariamo l'iteratore nel nuovo scope
                self.enter_scope()
                self.declare_var(iterator) # 'i' è visibile dentro il loop
                
                # Header del for
                header = f"for (let {iterator} = {js_start}; {iterator} < {js_end}; {iterator}++)"
                
                result = f"{indent}{header} {{\n"
                result += self.generate(body) + "\n"
                
                self.exit_scope()
                result += f"{indent}}}"
                return result

            # --- Funzioni ---
            case FunctionDecl(name, params, body):
                indent = self.get_indent()
                params_str = ", ".join(params)
                
                self.declare_var(name) # La funzione è visibile nello scope corrente
                
                result = f"{indent}function {name}({params_str}) {{\n"
                
                self.enter_scope()
                # I parametri sono variabili dichiarate nello scope della funzione
                for p in params:
                    self.declare_var(p)
                    
                result += self.generate(body) + "\n"
                self.exit_scope()
                
                result += f"{indent}}}"
                return result

            case FunctionCall(name, args):
                js_args = ", ".join([self.generate(arg) for arg in args])
                return f"{name}({js_args})"

            case None:
                return ""
            
            case _:
                raise Exception(f"Codegen Error: Unknown node '{node}'")

# --- TEST ---
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