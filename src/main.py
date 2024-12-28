# File: src/main.py

from lexer import Lexer
from parser import Parser
from obfuscator import Obfuscator
from deobfuscator import Deobfuscator
from code_generator import CodeGenerator
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    
    # Debug: Print tokens
    print("Tokens:")
    for token in tokens:
        print(token)
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    # Debug: Print AST
    print("\nAbstract Syntax Tree (AST):")
    print(ast)
    
    obfuscator = Obfuscator()
    obf_ast = obfuscator.obfuscate(ast)
    
    generator = CodeGenerator()
    obf_code = generator.generate(obf_ast)
    with open('obfuscated_code.c', 'w') as f:
        f.write(obf_code)
    print("\nObfuscated code generated as obfuscated_code.c")
    
    deobfuscator = Deobfuscator(obfuscator.identifier_map)
    deobf_ast = deobfuscator.deobfuscate(obf_ast)
    
    original_code = generator.generate(deobf_ast)
    with open('deobfuscated_code.c', 'w') as f:
        f.write(original_code)
    print("Deobfuscated code generated as deobfuscated_code.c")

if __name__ == "__main__":
    main()