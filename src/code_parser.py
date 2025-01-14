# src/code_parser.py

import re  # Imported to handle regular expressions in preprocessor directives
from lexer import Lexer, Token
from collections import namedtuple

class ASTNode:
    def __init__(self, type, value=None, children=None):
        """
        Initializes an ASTNode.
        
        Args:
            type (str): Type of the AST node (e.g., 'FunctionDeclaration', 'IfStatement').
            value (str, optional): Optional value associated with the node (e.g., variable name).
            children (list, optional): List of child ASTNodes.
        """
        self.type = type
        self.value = value
        self.children = children or []

    def __repr__(self, level=0):
        """
        Provides a string representation of the AST for debugging purposes.
        
        Args:
            level (int, optional): Current indentation level.
        
        Returns:
            str: String representation of the ASTNode.
        """
        ret = "  " * level + f"{self.type}"
        if self.value:
            ret += f": {self.value}"
        ret += "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

    def to_dict(self):
        """
        Recursively converts the ASTNode and its children into a dictionary.
        
        Returns:
            dict: A dictionary representation of the ASTNode.
        """
        node_dict = {
            'type': self.type,
            'value': self.value,
            'children': [child.to_dict() for child in self.children] if self.children else []
        }
        return node_dict

class Parser:
    def __init__(self, tokens):
        """
        Initializes the Parser with a list of tokens.
        
        Args:
            tokens (list): List of tokens obtained from the Lexer.
        """
        self.tokens = tokens
        self.position = 0

    def parse(self):
        """
        Initiates the parsing process and returns the root of the AST.
        
        Returns:
            ASTNode: The root node representing the program.
        """
        return self.program()

    def program(self):
        """
        Parses the entire program and constructs the root AST node.
        
        Returns:
            ASTNode: The root node representing the program.
        """
        statements = []
        while not self.current_token().type == 'EOF':
            if self.current_token().type == 'PREPROCESSOR':
                stmt = self.preprocessor_directive()
                statements.append(stmt)
            else:
                stmt = self.statement()
                statements.append(stmt)
        return ASTNode('Program', children=statements)

    def statement(self):
        """
        Parses a single statement based on the current token.
        
        Returns:
            ASTNode: The AST node representing the parsed statement.
        """
        token = self.current_token()
        if token.type in {'INT', 'FLOAT', 'VOID', 'CHAR', 'DOUBLE'}:
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
            next_token = self.peek_token()
            if next_token.type == 'LPAREN':
                return self.function_call_statement()
            else:
                return self.assignment_statement()
        elif token.type == 'IF':
            return self.if_statement()
        elif token.type == 'WHILE':
            return self.while_statement()
        elif token.type == 'RETURN':
            return self.return_statement()
        else:
            raise RuntimeError(f'Unexpected token {token.type} at line {token.line}, column {token.column}')

    def preprocessor_directive(self):
        """
        Parses a preprocessor directive (e.g., #include, #define).
        
        Returns:
            ASTNode: The AST node representing the preprocessor directive.
        """
        token = self.consume('PREPROCESSOR')
        directive, value = self.parse_preprocessor(token.value)
        return ASTNode('PreprocessorDirective', value=directive, children=[
            ASTNode('Value', value=value)
        ])

    def parse_preprocessor(self, directive):
        """
        Parses the preprocessor directive string to extract relevant information.
        
        Args:
            directive (str): The preprocessor directive (e.g., '#include <stdio.h>').
        
        Returns:
            tuple: A tuple containing the directive type and its associated value.
        """
        if directive.startswith('#include'):
            match = re.match(r'#\s*include\s*[\"<](.*)[\">]', directive)
            if match:
                return 'include', match.group(1)
        elif directive.startswith('#define'):
            parts = directive.split(maxsplit=2)
            if len(parts) >= 3:
                return 'define', ' '.join(parts[1:])
        return 'unknown', directive

    def declaration(self):
        """
        Parses a variable declaration.
        
        Returns:
            ASTNode: The AST node representing the variable declaration.
        """
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
        """
        Parses a function declaration.
        
        Returns:
            ASTNode: The AST node representing the function declaration.
        """
        return_type = self.consume().value  # Consume return type
        func_name = self.consume('IDENT').value  # Consume function name
        self.consume('LPAREN')  # Consume '('
        parameters = self.parameter_list()
        self.consume('RPAREN')  # Consume ')'
        self.consume('LBRACE')  # Consume '{'
        body = []
        while not self.current_token().type == 'RBRACE':
            body.append(self.statement())
        self.consume('RBRACE')  # Consume '}'
        return ASTNode('FunctionDeclaration', value=func_name, children=[
            ASTNode('ReturnType', value=return_type),
            ASTNode('Parameters', children=parameters),
            ASTNode('Body', children=body)
        ])

    def function_call_statement(self):
        """
        Parses a function call as a statement.
        
        Returns:
            ASTNode: The AST node representing the function call.
        """
        func_call = self.function_call()
        self.consume('SEMICOLON')  # Consume ';' after function call
        return ASTNode('FunctionCallStatement', children=[func_call])

    def function_call(self):
        """
        Parses a function call.
        
        Returns:
            ASTNode: The AST node representing the function call.
        """
        func_name = self.consume('IDENT').value  # Consume function name
        self.consume('LPAREN')  # Consume '('
        arguments = self.argument_list()
        self.consume('RPAREN')  # Consume ')'
        return ASTNode('FunctionCall', value=func_name, children=arguments)

    def argument_list(self):
        """
        Parses the list of arguments in a function call.
        
        Returns:
            list: A list of ASTNodes representing each argument.
        """
        arguments = []
        if self.current_token().type != 'RPAREN':
            while True:
                arg = self.expression()
                arguments.append(arg)
                if self.current_token().type == 'COMMA':
                    self.consume('COMMA')  # Consume ','
                else:
                    break
        return arguments

    def parameter_list(self):
        """
        Parses the list of parameters in a function declaration.
        
        Returns:
            list: A list of ASTNodes representing each parameter.
        """
        parameters = []
        if self.current_token().type in {'INT', 'FLOAT', 'VOID', 'CHAR', 'DOUBLE'}:
            while True:
                param_type = self.consume().value
                param_name = self.consume('IDENT').value
                parameters.append(ASTNode('Parameter', value=param_name, children=[
                    ASTNode('Type', value=param_type)
                ]))
                if self.current_token().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        return parameters

    def assignment_statement(self):
        """
        Parses an assignment statement.
        
        Returns:
            ASTNode: The AST node representing the assignment.
        """
        var_name = self.consume('IDENT').value
        self.consume('OP', '=')  # Expect '='
        expr = self.expression()
        self.consume('SEMICOLON')  # Expect ';'
        return ASTNode('AssignmentStatement', value=var_name, children=[expr])

    def if_statement(self):
        """
        Parses an 'if' statement.
        
        Returns:
            ASTNode: The AST node representing the 'if' statement.
        """
        self.consume('IF')
        self.consume('LPAREN')
        condition = self.expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        then_branch = []
        while not (self.current_token().type == 'RBRACE'):
            then_branch.append(self.statement())
        self.consume('RBRACE')
        return ASTNode('IfStatement', children=[
            condition,
            ASTNode('Then', children=then_branch)
        ])

    def while_statement(self):
        """
        Parses a 'while' loop.
        
        Returns:
            ASTNode: The AST node representing the 'while' loop.
        """
        self.consume('WHILE')
        self.consume('LPAREN')
        condition = self.expression()
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while not (self.current_token().type == 'RBRACE'):
            body.append(self.statement())
        self.consume('RBRACE')
        return ASTNode('WhileStatement', children=[
            condition,
            ASTNode('Body', children=body)
        ])

    def return_statement(self):
        """
        Parses a 'return' statement.
        
        Returns:
            ASTNode: The AST node representing the 'return' statement.
        """
        self.consume('RETURN')  # Consume 'return' token
        if self.current_token().type != 'SEMICOLON':
            expr = self.expression()  # Parse the expression to return
            self.consume('SEMICOLON')  # Consume ';'
            return ASTNode('ReturnStatement', children=[expr])
        else:
            self.consume('SEMICOLON')  # Consume ';'
            return ASTNode('ReturnStatement')

    def expression(self):
        """
        Parses an expression.
        
        Returns:
            ASTNode: The AST node representing the expression.
        """
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.current_token().type == 'OP' and self.current_token().value == '||':
            op = self.consume().value
            right = self.logical_and()
            node = ASTNode('LogicalOr', op, [node, right])
        return node

    def logical_and(self):
        node = self.equality()
        while self.current_token().type == 'OP' and self.current_token().value == '&&':
            op = self.consume().value
            right = self.equality()
            node = ASTNode('LogicalAnd', op, [node, right])
        return node

    def equality(self):
        node = self.relational()
        while self.current_token().type == 'OP' and self.current_token().value in {'==', '!='}:
            op = self.consume().value
            right = self.relational()
            node = ASTNode('Equality', op, [node, right])
        return node

    def relational(self):
        node = self.additive()
        while self.current_token().type == 'OP' and self.current_token().value in {'<', '>', '<=', '>='}:
            op = self.consume().value
            right = self.additive()
            node = ASTNode('Relational', op, [node, right])
        return node

    def additive(self):
        node = self.multiplicative()
        while self.current_token().type == 'OP' and self.current_token().value in {'+', '-'}:
            op = self.consume().value
            right = self.multiplicative()
            node = ASTNode('Additive', op, [node, right])
        return node

    def multiplicative(self):
        node = self.unary()
        while self.current_token().type == 'OP' and self.current_token().value in {'*', '/'}:
            op = self.consume().value
            right = self.unary()
            node = ASTNode('Multiplicative', op, [node, right])
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
        """
        Parses a primary expression.
        
        Returns:
            ASTNode: The AST node representing the primary expression.
        """
        token = self.current_token()
        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return ASTNode('Number', value=token.value)
        elif token.type == 'STRING':
            self.consume('STRING')
            return ASTNode('String', value=token.value)
        elif token.type == 'IDENT':
            next_token = self.peek_token()
            if next_token.type == 'LPAREN':
                return self.function_call()
            else:
                self.consume('IDENT')
                return ASTNode('Identifier', value=token.value)
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.expression()
            self.consume('RPAREN')
            return expr
        else:
            raise RuntimeError(f'Unexpected token {token.type} in expression at line {token.line}, column {token.column}')

    def current_token(self):
        """
        Retrieves the current token based on the parser's position.
        
        Returns:
            Token: The current token or an EOF token if at the end.
        """
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return Token('EOF', '', -1, -1)

    def peek_token(self, offset=1):
        """
        Peeks ahead in the token list without consuming tokens.
        
        Args:
            offset (int, optional): The number of tokens to look ahead.
        
        Returns:
            Token: The token at the peeked position or an EOF token if out of bounds.
        """
        peek_position = self.position + offset
        if peek_position < len(self.tokens):
            return self.tokens[peek_position]
        return Token('EOF', '', -1, -1)

    def consume(self, expected_type=None, expected_value=None):
        """
        Consumes the current token and advances the parser's position.
        
        Args:
            expected_type (str, optional): The expected type of the token.
            expected_value (str, optional): The expected value of the token.
        
        Returns:
            Token: The consumed token.
        
        Raises:
            RuntimeError: If the token doesn't match the expected type or value.
        """
        token = self.current_token()
        if expected_type and token.type != expected_type:
            raise RuntimeError(f'Expected token type {expected_type}, got {token.type} ("{token.value}") at line {token.line}, column {token.column}')
        if expected_value and token.value != expected_value:
            raise RuntimeError(f'Expected token value "{expected_value}", got "{token.value}" at line {token.line}, column {token.column}')
        self.position += 1
        return token

    def get_parse_tree(self):
        """
        Converts the AST into a JSON-serializable dictionary.
        
        Returns:
            dict: The parse tree in dictionary format.
        """
        ast_root = self.parse()
        return ast_root.to_dict()