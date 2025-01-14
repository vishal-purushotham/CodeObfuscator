from lexer import Lexer
from code_parser import Parser
from obfuscator import Obfuscator
from deobfuscator import Deobfuscator
from code_generator import CodeGenerator
import sys
import os
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file1.c> <source_file2.c> ...")
        sys.exit(1)
    
    source_files = sys.argv[1:]
    asts = []
    identifier_map = {}
    
    # Process each source file
    for file_path in source_files:
        if not os.path.isfile(file_path):
            print(f"File not found: {file_path}")
            continue
        
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        lexer = Lexer(source_code)
        try:
            tokens = lexer.tokenize()
        except RuntimeError as e:
            print(f"Lexing Error in {file_path}: {e}")
            continue
        
        # Debug: Print tokens
        print(f"Tokens for {file_path}:")
        for token in tokens:
            print(token)
        
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            asts.append((file_path, ast))
        except RuntimeError as e:
            print(f"Parsing Error in {file_path}: {e}")
            continue
        
        # Debug: Print AST
        print(f"\nAbstract Syntax Tree (AST) for {file_path}:")
        print(ast)
    
    if not asts:
        print("No valid source files to process.")
        sys.exit(1)
    
    obfuscator = Obfuscator()
    
    # Obfuscate all ASTs while maintaining a global identifier map
    for file_path, ast in asts:
        try:
            obfuscator.obfuscate(ast)
        except Exception as e:
            print(f"Obfuscation Error in {file_path}: {e}")
            continue
    
    generator = CodeGenerator()
    
    # Generate obfuscated code for each file
    for file_path, ast in asts:
        try:
            obf_code = generator.generate(ast)
        except Exception as e:
            print(f"Code Generation Error in {file_path}: {e}")
            continue
        
        obf_file_path = f"obfuscated_{os.path.basename(file_path)}"
        with open(obf_file_path, 'w') as f:
            f.write(obf_code)
        print(f"\nObfuscated code generated as {obf_file_path}")
    
    # Save the global identifier map
    identifier_map_file = 'identifier_map.json'
    with open(identifier_map_file, 'w') as f:
        json.dump(obfuscator.identifier_map, f, indent=4)
    print(f"Identifier map saved as {identifier_map_file}")
    
    # Optional: Deobfuscation Process
    deobfuscator = Deobfuscator(obfuscator.identifier_map)
    for obf_file in [f"obfuscated_{os.path.basename(f)}" for f in source_files]:
        if not os.path.isfile(obf_file):
            print(f"Obfuscated file not found: {obf_file}")
            continue
        
        with open(obf_file, 'r') as f:
            obf_code = f.read()
        
        lexer = Lexer(obf_code)
        try:
            tokens = lexer.tokenize()
        except RuntimeError as e:
            print(f"Lexing Error in {obf_file}: {e}")
            continue
        
        parser = Parser(tokens)
        try:
            obf_ast = parser.parse()
        except RuntimeError as e:
            print(f"Parsing Error in {obf_file}: {e}")
            continue
        
        try:
            deobf_ast = deobfuscator.deobfuscate(obf_ast)
        except Exception as e:
            print(f"Deobfuscation Error in {obf_file}: {e}")
            continue
        
        try:
            original_code = generator.generate(deobf_ast)
        except Exception as e:
            print(f"Code Generation Error in {obf_file}: {e}")
            continue
        
        deobf_file_path = f"deobfuscated_{os.path.basename(f)}"
        with open(deobf_file_path, 'w') as f:
            f.write(original_code)
        print(f"Deobfuscated code generated as {deobf_file_path}")

if __name__ == "__main__":
    main()