import ply.lex as lex

# ------------Token declaration------------
reserved = {
  # 'key': 'value'
  # 'python keyword': 'name of corresponding token'
    'int': 'TYPE_INT',
    'str': 'TYPE_STR',
    'bool': 'TYPE_BOOL',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
    'for': 'FOR',
    'in': 'IN',
    'range': 'RANGE',
    'input': 'INPUT',
    'print': 'PRINT',
    'def': 'DEF',
    'return': 'RETURN',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'True': 'TRUE',
    'False': 'FALSE'
}

tokens = [
    # Tokens names for operators without reserved keywords
    'ID',
    'NUMBER',
    'STRING',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQ',
    'NEQ',
    'LE',
    'GE',
    'LT',
    'GT',
    'ASSIGN',
    'LPAREN',
    'RPAREN',
    'COLON',
    'COMMA',
    'INDENT',
    'DEDENT',
    'NEWLINE'
] + list(reserved.values())

# -----------------------------------------

# ---------------Simple Rules--------------
# Prefix t_ + Token_name = r'Regex'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_EQ = r'=='
t_NEQ = r'!='
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'

t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
t_COMMA = r','

# -----------------------------------------

# --------------Complex Rules--------------
# Prefix t_ + Token_name(token): r'Regex' and operations

# Identify variable names
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Identify integer numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Identify strings
def t_STRING(t):
    r'(\"([^\\\n]|(\\.))*?\")|(\'([^\\\n]|(\\.))*?\')'
    t.value = t.value[1:-1]
    return t

# Identify new lines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NEWLINE'
    return t

# Identify unrecognised characters and skip them
def t_error(t):
    print(f"Illegal character '{t.value[0]}' in line {t.lexer.lineno}")
    t.lexer.skip(1)

# Characters to ignore
t_ignore = ' '
t_ignore_COMMENT = r'\#.*'