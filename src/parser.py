from lexer import Lexer, Token
from collections import namedtuple

class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f'ASTNode({self.type}, {self.value}, {self.children})'

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
    
    def parse(self):
        return self.program()
    
    def program(self):
        statements = []
        while not self.current_token().type == 'EOF':
            stmt = self.statement()
            statements.append(stmt)
        return ASTNode('Program', children=statements)
    
    def statement(self):
        token = self.current_token()
        if token.type in {'INT', 'FLOAT', 'VOID'}:
            # Lookahead to determine if it's a function or variable declaration
            next_token = self.peek_token()
            if next_token.type == 'IDENT':
                third_token = self.peek_token(2)
                if third_token.type == 'LPAREN':
                    return self.function_declaration()
                else:
                    return self.declaration()
            else:
                raise RuntimeError(f'Unexpected token {next_token.type} after {token.type} at line {token.line}')
        elif token.type == 'IDENT':
            return self.assignment()
        elif token.type == 'IF':
            return self.if_statement()
        elif token.type == 'WHILE':
            return self.while_statement()
        else:
            raise RuntimeError(f'Unexpected token {token.type} at line {token.line}')
    
    def declaration(self):
    var_type = self.consume().value  # Consume the type (e.g., 'int', 'float')
    var_name = self.consume('IDENT').value  # Consume the identifier (e.g., 'a')

    # Check if the next token is an assignment operator '='
    if self.current_token().type == 'OP' and self.current_token().value == '=':
        self.consume('OP')  # Consume '='
        expr = self.expression()  # Parse the expression on the right-hand side
        self.consume('SEMICOLON')  # Consume ';'
        return ASTNode('Declaration', value=var_name, children=[
            ASTNode('Type', value=var_type),
            ASTNode('Assignment', children=[expr])
        ])
    else:
        # If there's no assignment, just consume the semicolon
        self.consume('SEMICOLON')
        return ASTNode('Declaration', value=var_name, children=[
            ASTNode('Type', value=var_type)
        ])
    
    def function_declaration(self):
        var_type = self.consume().value  # Consume return type
        func_name = self.consume('IDENT').value  # Consume function name
        self.consume('LPAREN')  # Consume '('
        parameters = self.parameter_list()
        self.consume('RPAREN')  # Consume ')'
        self.consume('LBRACE')  # Consume '{'
        body = []
        while not self.current_token().type == 'RBRACE':
            body.append(self.statement())
        self.consume('RBRACE')  # Consume '}'
        return ASTNode('FunctionDeclaration', value=func_name, children=[ASTNode('ReturnType', value=var_type), ASTNode('Parameters', children=parameters), ASTNode('Body', children=body)])
    
    def parameter_list(self):
        parameters = []
        if self.current_token().type in {'INT', 'FLOAT', 'VOID'}:
            while True:
                param_type = self.consume().value
                param_name = self.consume('IDENT').value
                parameters.append(ASTNode('Parameter', value=param_name, children=[ASTNode('Type', value=param_type)]))
                if self.current_token().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        return parameters
    
    def assignment(self):
        var_name = self.consume('IDENT').value
        self.consume('OP', '=')
        expr = self.expression()
        self.consume('SEMICOLON')
        return ASTNode('Assignment', value=var_name, children=[expr])
    
    def if_statement(self):
        self.consume('IF')
        self.consume('LPAREN')
        condition = self.expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        then_branch = []
        while not (self.current_token().type == 'RBRACE'):
            then_branch.append(self.statement())
        self.consume('RBRACE')
        return ASTNode('If', children=[condition, ASTNode('Then', children=then_branch)])
    
    def while_statement(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while not (self.current_token().type == 'RBRACE'):
            body.append(self.statement())
        self.consume('RBRACE')
        return ASTNode('While', children=[condition, ASTNode('Body', children=body)])
    
    def expression(self):
        return self.logical_or()
    
    def logical_or(self):
        node = self.logical_and()
        while self.current_token().type == 'OP' and self.current_token().value == '||':
            op = self.consume().value
            right = self.logical_and()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def logical_and(self):
        node = self.equality()
        while self.current_token().type == 'OP' and self.current_token().value == '&&':
            op = self.consume().value
            right = self.equality()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def equality(self):
        node = self.relational()
        while self.current_token().type == 'OP' and self.current_token().value in {'==', '!='}:
            op = self.consume().value
            right = self.relational()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def relational(self):
        node = self.additive()
        while self.current_token().type == 'OP' and self.current_token().value in {'<', '>', '<=', '>='}:
            op = self.consume().value
            right = self.additive()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def additive(self):
        node = self.multiplicative()
        while self.current_token().type == 'OP' and self.current_token().value in {'+', '-'}:
            op = self.consume().value
            right = self.multiplicative()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def multiplicative(self):
        node = self.unary()
        while self.current_token().type == 'OP' and self.current_token().value in {'*', '/'}:
            op = self.consume().value
            right = self.unary()
            node = ASTNode('BinOp', op, [node, right])
        return node
    
    def unary(self):
        token = self.current_token()
        if token.type == 'OP' and token.value in {'-', '!'}:
            op = self.consume().value
            operand = self.unary()
            return ASTNode('UnaryOp', op, [operand])
        else:
            return self.primary()
    
    def primary(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return ASTNode('Number', value=token.value)
        elif token.type == 'STRING':
            self.consume('STRING')
            return ASTNode('String', value=token.value)
        elif token.type == 'IDENT':
            self.consume('IDENT')
            return ASTNode('Identifier', value=token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.expression()
            self.consume('RPAREN')
            return expr
        else:
            raise RuntimeError(f'Unexpected token {token.type} in expression at line {token.line}')
    
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return Token('EOF', '', -1, -1)
    
    def peek_token(self, offset=1):
        peek_position = self.position + offset
        if peek_position < len(self.tokens):
            return self.tokens[peek_position]
        return Token('EOF', '', -1, -1)
    
    def consume(self, expected_type=None, expected_value=None):
        token = self.current_token()
        if expected_type and token.type != expected_type:
            raise RuntimeError(f'Expected token type {expected_type}, got {token.type} at line {token.line}')
        if expected_value and token.value != expected_value:
            raise RuntimeError(f'Expected token value {expected_value}, got {token.value} at line {token.line}')
        self.position += 1
        return token