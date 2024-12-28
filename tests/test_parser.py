import sys
import pytest
from src.lexer import Lexer  # Updated import path
from src.parser import Parser  # Added import for Parser

def test_parse_declaration():
    source = "int a;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assert ast.type == 'Program'
    assert len(ast.children) == 1
    decl = ast.children[0]
    assert decl.type == 'Declaration'
    assert decl.value == 'a'
    assert decl.children[0].type == 'Type'
    assert decl.children[0].value == 'int'

def test_parse_assignment():
    source = "a = 5 + 3;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    assign = ast.children[0]
    assert assign.type == 'Assignment'
    assert assign.value == 'a'
    expr = assign.children[0]
    assert expr.type == 'BinOp'
    assert expr.value == '+'