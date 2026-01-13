import ply.lex as lex

errors = []

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
    # Tokens name for operators without reserved keywords
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

# ---------------Simple rules--------------
# prefix t_ + token_name = r'regex'

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

# --------------Complex rules--------------
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
    error_msg = f"Illegal character '{t.value[0]}' in line {t.lexer.lineno}"
    print(error_msg)
    errors.append(error_msg)
    t.lexer.skip(1)

# Characters to ignore
t_ignore = ' '
t_ignore_COMMENT = r'\#.*'

# -----------------------------------------

# --------------Indent Lexer---------------
class IndentLexer:
    """
    Wrapper for the standard PLY Lexer. It uses the standard PLY Lexer as a base component but it handles the spacing introducing
    the INDENT and DEDENT.
    """
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_stream = None

    def input(self, data):
        """
        Inputs data to the lexer and initialize the filtering process
        """
        self.lexer.input(data)
        self.token_stream = self.filter()

    def token(self):
        """
        Return the next token from the filtered token stream
        """
        try:
            return next(self.token_stream)
        except StopIteration:
            return None
        
    def filter(self):
        """
        Iterates over the tokens and inserts INDENT or DEDENT tokens for the spacing or newlines handling
        """
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

                while self.lexer.lexpos < len(self.lexer.lexdata) and self.lexer.lexdata[self.lexer.lexpos] == ' ':
                    indent_level += 1
                    self.lexer.lexpos += 1
                
                current_level = indent_stack[-1]

                if indent_level > current_level:
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

# --------Just for testing purposes--------
def find_column(input_text, token):
    """
    Helper function that computes the column of each token
    """
    line_start = input_text.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

if __name__ == '__main__':
    data = '''groupSize = 2
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


    '''

    lexer.input(data)
        
    print("---START LEXER TEST---")
        
    # Table header
    header = f"| {'TYPE':<15} | {'VALUE':<25} | {'LINE':<5} | {'COL':<5} | {'POS':<5} |"
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    while True:
        tok = lexer.token()
        if not tok: 
            break

        # Compute column
        col = find_column(data, tok)
        
        # Format the value
        val = repr(tok.value)

        # Cut if too long not to break the table
        if len(val) > 23:
            val = val[:20] + "..."

        # Print the table
        print(f"| {tok.type:<15} | {val:<25} | {tok.lineno:<5} | {col:<5} | {tok.lexpos:<5} |")

    print("-" * len(header))
    print("---TEST LEXER END---")