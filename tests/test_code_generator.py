import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.code_generator import CodeGenerator

def test_generate_code():
    source = "int a = 5 + 3;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    generator = CodeGenerator()
    code = generator.generate(ast)
    expected = "int a;\na = (5 + 3);"
    assert code.strip() == expected