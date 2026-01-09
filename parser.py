import ply.yacc as yacc
from lexer import tokens, lexer
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Any
import pprint

errors = []

# --------------Dataclass definiment---------------
Expr = Any

@dataclass
class Number:
    value: int

@dataclass
class String:
    value: str

@dataclass
class Boolean:
    value: str

@dataclass
class BinOp:
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryOp:
    op: str
    expr: Expr
    
@dataclass
class AssignStat:
    name: str
    value: Expr

@dataclass
class PrintStat:
    value: Expr

@dataclass
class ReturnStat:
    value: Expr

@dataclass
class Var:
    name: str

@dataclass
class InputExpr:
    prompt: str

@dataclass
class FunctionCall:
    name: str
    args: List[Expr] = field(default_factory=list)

@dataclass
class ExprStat:
    expr: Expr

@dataclass
class IfStat:
    condition: Expr
    true_block: List[Any]
    false_block: Optional[List[Any]] = None  # false_block is defined only if Else statement is present

@dataclass
class ForStat:
    iterator: str
    start: Expr
    end: Expr
    body: List[Any]

@dataclass
class FunctionDecl:
    name: str # function name
    params: List[str] # List of parameters
    body: List[Any] # block of code of the function

# -----------------------------------------

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('nonassoc', 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'UMINUS') # Unary MINUS
)

# -----------Basic grammar rules-----------
def p_program(p):
    '''program : statements'''
    p[0] = p[1]

def p_statements_multi(p):
    '''statements : statements statement'''
    if p[2] is not None:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = p[1]
    
def p_statements_single(p):
    '''statements : statement'''
    if p[1] is not None:
        p[0] = [p[1]]
    else: 
        p[0] = []

def p_statement_newline(p):
    '''statement : NEWLINE'''
    p[0] = None

def p_statement_assign(p):
    '''statement : ID ASSIGN expression NEWLINE'''
    p[0] = AssignStat(p[1], p[3])

def p_statement_print(p):
    '''statement : PRINT LPAREN expression RPAREN NEWLINE'''
    p[0] = PrintStat(p[3])

def p_statement_return(p):
    '''statement : RETURN expression NEWLINE'''
    p[0] = ReturnStat(p[2])

def p_statement_if(p):
    '''statement : IF expression COLON block
                 | IF expression COLON block ELSE COLON block'''
    if len(p) == 5: 
        p[0] = IfStat(p[2], p[4]) 
    else:
        p[0] = IfStat(p[2], p[4], p[7])

def p_statement_elif(p):
    '''statement : IF expression COLON block elif_blocks'''
    p[0] = IfStat(p[2], p[4], p[5])

def p_elif_blocks(p):
    '''elif_blocks : ELIF expression COLON block elif_blocks
                   | ELIF expression COLON block ELSE COLON block
                   | ELIF expression COLON block'''
    if len(p) == 6:
        p[0] = [IfStat(p[2], p[4], p[5])] if p[5] else [IfStat(p[2], p[4])]
    elif len(p) == 8:
        p[0] = [IfStat(p[2], p[4], p[7])]
    elif len(p) == 5:
        p[0] = [IfStat(p[2], p[4])]

def p_block(p):
    '''block : NEWLINE INDENT statements DEDENT'''
    p[0] = p[3]

def p_statement_for(p):
    '''statement : FOR ID IN RANGE LPAREN expression RPAREN COLON block
                 | FOR ID IN RANGE LPAREN expression COMMA expression RPAREN COLON block'''
    if len(p) == 10:
        p[0] = ForStat(p[2], Number(0), p[6], p[9])
    else:
        p[0] = ForStat(p[2], p[6], p[8], p[11])

def p_statement_def(p):
    '''statement : DEF ID LPAREN parameters RPAREN COLON block'''
    p[0] = FunctionDecl(p[2], p[4], p[7])

def p_parameters(p):
    '''parameters : parameters COMMA ID
                  | ID
                  | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_statement_expr(p):
    '''statement : expression NEWLINE'''
    p[0] = ExprStat(p[1])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression GT expression
                  | expression LT expression
                  | expression GE expression
                  | expression LE expression
                  | expression EQ expression
                  | expression NEQ expression
                  | expression AND expression
                  | expression OR expression'''
    p[0] = BinOp(p[1], p[2], p[3])

def p_expression_unary(p):
    '''expression : MINUS  expression %prec UMINUS
                  | NOT expression'''
    p[0] = UnaryOp(p[1], p[2])

def p_expression_call(p):
    '''expression : ID LPAREN arguments RPAREN'''
    p[0] = FunctionCall(p[1], p[3])

def p_arguments(p):
    '''arguments : arguments COMMA expression
                 | expression
                 | empty'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else: 
        p[0] = []

def p_expression_input(p):
    '''expression : INPUT LPAREN STRING RPAREN'''
    p[0] = InputExpr(p[3])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = Number(p[1])

def p_expression_string(p):
    '''expression : STRING'''
    p[0] = String(p[1])

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    p[0] = Boolean(p[1])

def p_expression_id(p):
    '''expression : ID'''
    p[0] = Var(p[1])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        error_msg = f"Syntax error for token '{p.value}' (line {p.lineno})"
        print(error_msg)
        errors.append(error_msg)
    else:
        error_msg = "Syntax error at the end of the file"
        print(error_msg)
        errors.append(error_msg)

# -----------------------------------------

# ---FIX FOR PYINSTALLER (.EXE PURPOSES)---
class SilentLogger:
    def warning(self, msg, *args, **kwargs): pass
    def error(self, msg, *args, **kwargs): pass
    def info(self, msg, *args, **kwargs): pass
    def debug(self, msg, *args, **kwargs): pass

# PLY writes on this silentlogger which does nothing. This prevents crashes due to the absence of console while using the gui.
parser = yacc.yacc(write_tables=False, debug=False, errorlog=SilentLogger())

# --------Just for testing purposes--------
if __name__ == '__main__':
    test_code = textwrap.dedent("""groupSize = 2
groupMember1 = "Andrea"
groupMember2 = 'Piergiuseppe'  # Test strings defined with single quotes
workingOnTranspiler = True
componentsToDevelop = 4
isWorkingHard = False

def encourage_team(member, status):
    if member == "Andrea" and not status:
        print("Andrea, wake up! We've got the lexer to do.")
        return 0
    elif member == "Piergiuseppe" or status == True:
        print("Great work, keep it up!")
        return 1
    else:
        return -1


if workingOnTranspiler:
    print("Starting coding session...")
    
    if groupSize == 2:
        print("The team is complete.")
        
        for i in range(componentsToDevelop):
            remaining = 4 - i
            print(remaining)
            
    print("Session ended.")
    """)

    print(f"--- SOURCE CODE ---\n{test_code}\n-----------------------")
    
    lexer.lineno = 1

    result = parser.parse(test_code, lexer=lexer)
    
    print("\n--- PARSER RESULT (AST) ---")
    if result:
        pprint.pprint(result)
        print("\n Parsing completed successfully!")
    else:
        print("\n Error during parsing (or empty input).")