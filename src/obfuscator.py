# Modified obfuscator.py

import string
import random
import json
import os

class Obfuscator:
    def __init__(self):
        self.identifier_map = {}
        self.reserved_keywords = {'if', 'else', 'while', 'return', 'int', 'float', 'void', 'char', 'double', 'include', 'define'}

    def obfuscate(self, ast):
        self._obfuscate_node(ast)
        return ast

    def _obfuscate_node(self, node):
        # Rename identifiers used in variable declarations
        if node.type == 'Declaration' or node.type == 'AssignmentStatement':
            original_name = node.value
            if original_name not in self.identifier_map and original_name not in self.reserved_keywords:
                self.identifier_map[original_name] = self._generate_random_name()
            if original_name in self.identifier_map:
                node.value = self.identifier_map[original_name]

        # Rename identifiers used elsewhere (e.g., in expressions)
        elif node.type == 'Identifier':
            original_name = node.value
            if original_name in self.identifier_map:
                node.value = self.identifier_map[original_name]

        # Handle function declarations
        elif node.type == 'FunctionDeclaration':
            func_name = node.value
            if func_name not in self.identifier_map and func_name not in self.reserved_keywords:
                self.identifier_map[func_name] = self._generate_random_name()
            if func_name in self.identifier_map:
                node.value = self.identifier_map[func_name]

            # Obfuscate parameters
            parameters = node.children[1].children  # Parameters are the second child
            for param in parameters:
                param_name = param.value
                if param_name not in self.identifier_map and param_name not in self.reserved_keywords:
                    self.identifier_map[param_name] = self._generate_random_name()
                if param_name in self.identifier_map:
                    param.value = self.identifier_map[param_name]

        # Handle preprocessor directives (e.g., #define)
        elif node.type == 'PreprocessorDirective':
            directive = node.value
            if directive.startswith('define'):
                parts = directive.split()
                if len(parts) >= 3:
                    macro_name = parts[1]
                    if macro_name not in self.identifier_map and macro_name not in self.reserved_keywords:
                        self.identifier_map[macro_name] = self._generate_random_name()
                    if macro_name in self.identifier_map:
                        # Update the directive with the obfuscated macro name
                        node.value = f'define {self.identifier_map[macro_name]} ' + ' '.join(parts[2:])

        for child in node.children:
            if child:
                self._obfuscate_node(child)

    def _generate_random_name(self, length=8):
        letters = string.ascii_letters
        # Ensure the first character is a letter or underscore
        first_char = random.choice(string.ascii_letters + "_")
        other_chars = ''.join(random.choice(letters + string.digits + "_") for _ in range(length - 1))
        return first_char + other_chars

    def save_identifier_map(self, filepath='identifier_map.json'):
        with open(filepath, 'w') as f:
            json.dump(self.identifier_map, f, indent=4)
        print(f"Identifier map saved to {filepath}")

    def load_identifier_map(self, filepath='identifier_map.json'):
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.identifier_map = json.load(f)
            print(f"Identifier map loaded from {filepath}")
        else:
            print(f"No identifier map found at {filepath}")