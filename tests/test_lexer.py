import sys
import pytest
from src.lexer import Lexer  # Updated import path

def test_tokenize_simple():
    source = "int a = 5;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    assert tokens[0].type == 'INT'
    assert tokens[1].type == 'IDENT'
    assert tokens[2].type == 'OP'
    assert tokens[3].type == 'NUMBER'
    assert tokens[4].type == 'OP'
    assert tokens[5].type == 'EOF'

def test_tokenize_invalid():
    source = "int @ = 5;"
    lexer = Lexer(source)
    with pytest.raises(RuntimeError):
        lexer.tokenize()