import ply.yacc as yacc
from lexer import tokens, lexer
import textwrap
from dataclasses import dataclass, field
from typing import List, Optional, Any
import pprint

# Nodi albero AST usando dataclass
Expr = Any # solo per chiarezza, a runtime è dinamico

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
    expr: Expr
    op: str

@dataclass
class AssignStat:  # Assegnamento di una variabile
    name: str
    value: Expr

@dataclass
class PrintStat:
    value: Expr

@dataclass
class Var: # per leggere la variabile
    name: str

@dataclass
class InputExpr:
    prompt: str

@dataclass
class FunctionCall:
    name: str # nome della funzione
    args: List[Expr] = field(default_factory=list) # lista di espressioni come argomenti

@dataclass
class ExprStat:
    expr: Expr

@dataclass
class IfStat:
    condition: Expr
    true_block: List[Any]
    # Opzionale: default è None. 
    false_block: Optional[List[Any]] = None 

@dataclass
class ForStat:
    iterator: str
    start: Expr
    end: Expr
    body: List[Any]

@dataclass
class FunctionDecl:
    name: str # nome della funzione
    params: List[str] # lista di nomi dei parametri
    body: List[Any] # blocco di codice della funzione

# precedenza degli operatori
precedence = (
    ('left', 'EQ', 'NEQ', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'), # + e - hanno meno precedenza
    ('left', 'TIMES', 'DIVIDE'), # * e / hanno più precedenza
)

# regola grammaticale base
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

def p_statement_assign(p): # regola per assegnamento di una variabile
    '''statement : ID ASSIGN expression NEWLINE'''
    # p[1] è il nome variabile, p[3] è il valore
    p[0] = AssignStat(p[1], p[3])

# regola per il print
def p_statement_print(p):
    '''statement : PRINT LPAREN expression RPAREN NEWLINE'''
    p[0] = PrintStat(p[3])

def p_statement_if(p):
    '''statement : IF expression COLON block
                 | IF expression COLON block ELSE COLON block'''
    if len(p) == 5: # Caso solo IF. Perchè proprio 5? Perchè c'è p[0]: statement, p[1]: IF, p[2]: expression (La condizione), p[3]: COLON, p[4]: block
        # Chiama IfStat(condition, true_block, false_block=None)
        p[0] = IfStat(p[2], p[4]) 
    else: # Caso IF-ELSE. Qui len(p) == 8
        # Chiama IfStat(condition, true_block, false_block=block_else)
        p[0] = IfStat(p[2], p[4], p[7])

def p_block(p):
    '''block : NEWLINE INDENT statements DEDENT'''
    # p[1] = NEWLINE, p[2] = INDENT, p[3] = statements (La lista di istruzioni), p[4] = DEDENT
    p[0] = p[3]

def p_statement_for(p):
    '''statement : FOR ID IN RANGE LPAREN expression COMMA expression RPAREN COLON block'''
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

# operazioni matematiche (BinOp)
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
                  | expression NEQ expression'''
    # p[1] è left, p[2] è op, p[3] è right
    p[0] = BinOp(p[1], p[2], p[3])

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

# parentesi nelle espressioni
def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

# numeri
def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = Number(p[1])

# stringhe
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

# gestione errori di sintassi
def p_error(p):
    if p:
        print(f"Errore di sintassi al token '{p.value}' (riga {p.lineno})")
    else:
        print("Errore di sintassi alla fine del file")

# costruisci il parser
parser = yacc.yacc()

# TEST - mancano le regole per gli if o def. abbiamo scritto solo per PRINT e MATEMATICA

if __name__ == '__main__':
    # Usiamo textwrap.dedent per rimuovere l'indentazione "estetica" della stringa
    test_code = textwrap.dedent("""
    x = 10
    limit = 5
    
    print("Inizio Controllo")

    if x > limit:
        print("Maggiore")
        bonus = x + 2
        print(bonus)
    else:
        print("Minore o uguale")
    print("Fine Programma")
    """) # Nota: textwrap pulisce tutto, quindi per il lexer 'x' sarà a colonna 0

    print(f"Analizzo:\n{test_code}\n---")
    result = parser.parse(test_code, lexer=lexer)
    
    print("Albero AST generato:")
    if result:
    # Passi direttamente tutta la lista 'result' a pprint
        pprint.pprint(result) 
    else:
        print("Nessun risultato (Errore di sintassi).")