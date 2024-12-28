import sys
import pytest
from src.lexer import Lexer  # Updated import path
from src.parser import Parser  # Added import for Parser
from src.obfuscator import Obfuscator  # Added import for Obfuscator
from src.deobfuscator import Deobfuscator  # Updated import path

def test_deobfuscate_identifiers():
    source = "int a = 5; float b = a + 3;"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    obfuscator = Obfuscator()
    obf_ast = obfuscator.obfuscate(ast)
    
    deobfuscator = Deobfuscator(obfuscator.identifier_map)
    deobf_ast = deobfuscator.deobfuscate(obf_ast)
    
    assign = deobf_ast.children[2]
    assert assign.value == 'a'