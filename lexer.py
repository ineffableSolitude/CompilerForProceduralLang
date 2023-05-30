from rply import LexerGenerator


class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('LITERAL', r'"[^\"]*"')
        self.lexer.add('AND', r'and')
        self.lexer.add('NOT', r'not')
        self.lexer.add('OR', r'or')
        self.lexer.add('IF', r'if')
        self.lexer.add('THEN', r'then')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('WHILE', r'while')
        self.lexer.add('DO', r'do')
        self.lexer.add('BREAK', r'break')
        self.lexer.add('CONTINUE', r'continue')
        self.lexer.add('BEGIN', r'\{')
        self.lexer.add('END', r'\}')
        self.lexer.add('INTEGER', r'integer')
        self.lexer.add('FLOAT', r'float')
        self.lexer.add('FUNCTION', r'function')
        self.lexer.add('VAR', r'var')
        self.lexer.add('PROGRAM', r'program')


        self.lexer.add('LEQUAL', r'\<=')
        self.lexer.add('GEQUAL', r'\>=')
        self.lexer.add('NOT_EQUAL', r'\!=')
        self.lexer.add('EQUALS', r'\:=')
        self.lexer.add('PRINT', r'print')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('SEMI_COLON', r'\;')
        self.lexer.add('COLON', r'\:')
        self.lexer.add('COMMA', r'\,')
        self.lexer.add('EQUAL', r'\=')
        self.lexer.add('GTHAN', r'\>')
        self.lexer.add('LTHAN', r'\<')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'\/')


        
        self.lexer.add('NUMBER', r'[0-9]+(\.[0-9]+)?')
        self.lexer.add('ID', r'[a-zA-Z]*')
        self.lexer.ignore(r'#[^\#]*#')
        self.lexer.ignore('\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
