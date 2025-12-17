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

# -----------------------------------------

# --------------Indent Lexer---------------
class IndentLexer:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_stream = None

    def input(self, data):
        self.lexer.input(data)
        self.token_stream = self.filter()

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None
        
    def filter(self):
        tokens = iter(self.lexer.token, None)

        indent_stack = [0]

        for token in tokens:
            if token.type == 'NEWLINE':
                yield token

                try:
                    next_char = self.lexer.lexdata[self.lexer.lexpos]
                except IndexError:
                    next_char = ''

                if next_char == '\n':
                    continue
                
                indent_level = 0

                # Qui c'è il problema del tab. Dobbiamo decidere se gestire anche i tab e se sostituirli con 4 spazi.
                while self.lexer.lexpos < len(self.lexer.lexdata) and self.lexer.lexdata[self.lexer.lexpos] == ' ':
                    indent_level += 1
                    self.lexer.lexpos += 1
                
                current_level = indent_stack[-1]

                if indent_level > indent_stack[-1]:
                    indent_stack.append(indent_level)
                    tok = lex.LexToken()
                    tok.type = 'INDENT'
                    tok.value = indent_level
                    tok.lineno = token.lineno
                    tok.lexpos = token.lexpos
                    yield tok
                
                elif indent_level < current_level:
                    while indent_level < indent_stack[-1]:
                        indent_stack.pop()
                        tok = lex.LexToken()
                        tok.type = 'DEDENT'
                        tok.value = indent_level
                        tok.lineno = token.lineno
                        tok.lexpos = token.lexpos
                        yield tok
                    
                    if indent_level != indent_stack[-1]:
                        print('Error: Indentation not aligned')
            
            else:
                yield token
                
        while len(indent_stack) > 1:
            indent_stack.pop()

            tok = lex.LexToken()
            tok.type = 'DEDENT'
            tok.value = indent_stack[-1]
            tok.lineno = self.lexer.lineno
            tok.lexpos = 0
            yield tok

# -----------------------------------------

raw_lexer = lex.lex()
lexer = IndentLexer(raw_lexer)