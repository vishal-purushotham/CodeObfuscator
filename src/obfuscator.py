# src/obfuscator.py

import string
import random
import json
import os

class Obfuscator:
    def __init__(self):
        """
        Initializes the Obfuscator with an empty identifier map and reserved keywords.
        """
        self.identifier_map = {}
        self.reserved_keywords = {
            'if', 'else', 'while', 'return', 'int', 'float',
            'void', 'char', 'double', 'include', 'define'
        }

    def obfuscate(self, ast):
        """
        Initiates the obfuscation process by traversing the AST and renaming identifiers.

        Args:
            ast (ASTNode): The root node of the AST.

        Returns:
            ASTNode: The obfuscated AST.
        """
        self._obfuscate_node(ast)
        return ast

    def _obfuscate_node(self, node):
        """
        Recursively traverses the AST nodes to obfuscate identifiers.

        Args:
            node (ASTNode): The current AST node being processed.
        """
        if node.type in {'Declaration', 'AssignmentStatement'}:
            # Rename variable identifiers
            original_name = node.value
            if self._should_obfuscate(original_name):
                self._add_to_identifier_map(original_name)
                node.value = self.identifier_map[original_name]

        elif node.type == 'Identifier':
            # Rename identifiers used elsewhere (e.g., in expressions)
            original_name = node.value
            if original_name in self.identifier_map:
                node.value = self.identifier_map[original_name]

        elif node.type == 'FunctionDeclaration':
            # Rename function identifiers
            func_name = node.value
            if self._should_obfuscate(func_name):
                self._add_to_identifier_map(func_name)
                node.value = self.identifier_map[func_name]

            # Obfuscate function parameters
            parameters = node.children[1].children  # Parameters are the second child
            for param in parameters:
                param_name = param.value
                if self._should_obfuscate(param_name):
                    self._add_to_identifier_map(param_name)
                    param.value = self.identifier_map[param_name]

        elif node.type == 'PreprocessorDirective':
            # Handle preprocessor directives (e.g., #define)
            directive = node.value
            if directive.startswith('define'):
                parts = directive.split()
                if len(parts) >= 3:
                    macro_name = parts[1]
                    if self._should_obfuscate(macro_name):
                        self._add_to_identifier_map(macro_name)
                        # Update the directive with the obfuscated macro name
                        node.value = f'define {self.identifier_map[macro_name]} ' + ' '.join(parts[2:])

        # Recursively process child nodes
        for child in node.children:
            if child:
                self._obfuscate_node(child)

    def _should_obfuscate(self, identifier):
        """
        Determines whether an identifier should be obfuscated.

        Args:
            identifier (str): The identifier to evaluate.

        Returns:
            bool: True if the identifier should be obfuscated, False otherwise.
        """
        return identifier not in self.identifier_map and identifier not in self.reserved_keywords

    def _add_to_identifier_map(self, original_name, length=8):
        """
        Adds an identifier to the identifier map with a generated obfuscated name.

        Args:
            original_name (str): The original identifier name.
            length (int, optional): Length of the obfuscated name. Defaults to 8.
        """
        if original_name not in self.identifier_map:
            obfuscated_name = self._generate_random_name(length)
            self.identifier_map[original_name] = obfuscated_name

    def _generate_random_name(self, length=8):
        """
        Generates a random identifier name.

        Args:
            length (int, optional): Length of the generated name. Defaults to 8.

        Returns:
            str: The generated random name.
        """
        letters = string.ascii_letters
        # Ensure the first character is a letter or underscore
        first_char = random.choice(string.ascii_letters + "_")
        other_chars = ''.join(random.choice(letters + string.digits + "_") for _ in range(length - 1))
        return first_char + other_chars

    def save_identifier_map(self, filepath='identifier_map.json'):
        """
        Saves the identifier map to a JSON file.

        Args:
            filepath (str, optional): Path to the JSON file. Defaults to 'identifier_map.json'.
        """
        with open(filepath, 'w') as f:
            json.dump(self.identifier_map, f, indent=4)
        print(f"Identifier map saved to {filepath}")

    def load_identifier_map(self, filepath='identifier_map.json'):
        """
        Loads the identifier map from a JSON file.

        Args:
            filepath (str, optional): Path to the JSON file. Defaults to 'identifier_map.json'.
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.identifier_map = json.load(f)
            print(f"Identifier map loaded from {filepath}")
        else:
            print(f"No identifier map found at {filepath}")