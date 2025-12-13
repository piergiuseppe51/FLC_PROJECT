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
    'LT',
    'GT',
    'LE',
    'GE',
    'LPAREN',
    'RPAREN',
    'ASSIGN',
    'COLON',
    'COMMA',
    'INDENT',
    'DEDENT',
    'NEWLINE'
] + list(reserved.values())

# -----------------------------------------