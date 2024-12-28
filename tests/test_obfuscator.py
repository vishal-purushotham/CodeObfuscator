import sys
import pytest
from src.lexer import Lexer  # Updated import path
from src.parser import Parser  # Added import for Parser
from src.obfuscator import Obfuscator  # Updated import path

def test_obfuscate_identifiers():
    source = "int a = 5; float b = a + 3;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    obfuscator = Obfuscator()
    obf_ast = obfuscator.obfuscate(ast)
    
    decl_a = obf_ast.children[0]
    decl_b = obf_ast.children[1]
    assign = obf_ast.children[2]
    
    assert decl_a.children[0].value.startswith('var_')
    assert decl_b.children[0].value.startswith('var_')
    assert assign.value.startswith('var_')