# src/lexer.py

import re
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []
        self.keywords = {'if', 'else', 'while', 'return', 'int', 'float', 'void', 'char', 'double', 'include', 'define'}
        self.token_specification = [
            ('COMMENT',        r'//.*|/\*[\s\S]*?\*/'),       # Single-line and multi-line comments
            ('PREPROCESSOR',   r'\#\s*(include|define)\s+["<][^">]+[">]'),  # Preprocessor directives
            ('NUMBER',         r'\d+(\.\d*)?'),               # Integer or decimal number
            ('IDENT',          r'[A-Za-z_]\w*'),              # Identifiers
            ('DOT',            r'\.'),          # Member access operator
            ('OP',             r'[+\-*/%=<>!&|]+'),           # Operators
            ('LPAREN',         r'\('),                         # Left Parenthesis
            ('RPAREN',         r'\)'),                         # Right Parenthesis
            ('LBRACE',         r'\{'),                         # Left Brace
            ('RBRACE',         r'\}'),                         # Right Brace
            ('SEMICOLON',      r';'),                          # Semicolon
            ('COMMA',          r','),                          # Comma
            ('STRING',         r'\".*?\"'),                    # String literals
            ('NEWLINE',        r'\n'),                         # Line endings
            ('SKIP',           r'[ \t]+'),                     # Skip spaces and tabs
            ('MISMATCH',       r'.'),                          # Any other character
        ]
        # Compile the regex patterns into a pattern object
        self.token_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specification))

    def tokenize(self):
        line_num = 1
        line_start = 0
        for mo in self.token_regex.finditer(self.source):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
                self.tokens.append(Token(kind, value, line_num, column))
            elif kind == 'IDENT':
                if value in self.keywords:
                    kind = value.upper()
                self.tokens.append(Token(kind, value, line_num, column))
            elif kind in {'OP', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMMA'}:
                self.tokens.append(Token(kind, value, line_num, column))
            elif kind == 'STRING':
                self.tokens.append(Token(kind, value[1:-1], line_num, column))  # Remove quotes
            elif kind == 'PREPROCESSOR':
                self.tokens.append(Token(kind, value, line_num, column))
            elif kind == 'NEWLINE':
                line_num += 1
                line_start = mo.end()
            elif kind == 'SKIP' or kind == 'COMMENT':
                continue  # Skip spaces, tabs, and comments
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
        self.tokens.append(Token('EOF', '', line_num, column))
        return self.tokens