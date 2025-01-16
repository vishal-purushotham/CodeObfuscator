# src/obfuscator.py

import string
import random
import json
import os
import logging

class Obfuscator:
    def __init__(self):
        """
        Initializes the Obfuscator with an empty identifier map and reserved keywords.
        """
        self.identifier_map = {}
        self.reserved_keywords = {
            'if', 'else', 'while', 'for', 'return', 'int', 'float',
            'void', 'char', 'double', 'include', 'define', 'switch',
            'case', 'default', 'do', 'sizeof', 'long', 'short',
            'unsigned', 'signed', 'goto', 'enum', 'extern',
            'register', 'volatile', 'union', 'auto', 'static', 'const',
            'break', 'continue', 'struct', 'typedef'
        }
        # Configure logging
        logging.basicConfig(
            filename='obfuscator.log',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s: %(message)s'
        )

    def obfuscate(self, ast):
        """
        Initiates the obfuscation process by traversing the AST and renaming identifiers.

        Args:
            ast (ASTNode): The root node of the AST.

        Returns:
            ASTNode: The obfuscated AST.
        """
        logging.debug("Starting obfuscation process.")
        self._obfuscate_node(ast)
        logging.debug(f"Obfuscation complete. Identifier map: {self.identifier_map}")
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
                logging.debug(f"Obfuscated identifier '{original_name}' to '{node.value}'.")

        elif node.type == 'Identifier':
            # Rename identifiers used elsewhere (e.g., in expressions)
            original_name = node.value
            if original_name in self.identifier_map:
                logging.debug(f"Deobfuscating identifier '{original_name}' to '{self.identifier_map[original_name]}'.")
                node.value = self.identifier_map[original_name]

        elif node.type == 'FunctionDeclaration':
            # Rename function identifiers
            func_name = node.value
            if self._should_obfuscate(func_name):
                self._add_to_identifier_map(func_name)
                node.value = self.identifier_map[func_name]
                logging.debug(f"Obfuscated function name '{func_name}' to '{node.value}'.")

            # Obfuscate function parameters
            parameters = node.children[1].children  # Parameters are the second child
            for param in parameters:
                param_name = param.value
                if self._should_obfuscate(param_name):
                    self._add_to_identifier_map(param_name)
                    param.value = self.identifier_map[param_name]
                    logging.debug(f"Obfuscated parameter name '{param_name}' to '{param.value}'.")

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
                        obf_macro = self.identifier_map[macro_name]
                        new_directive = f'define {obf_macro} ' + ' '.join(parts[2:])
                        node.value = new_directive
                        logging.debug(f"Obfuscated macro name '{macro_name}' to '{obf_macro}' in preprocessor directive.")

        # Ensure that operators are not altered by skipping them
        elif node.type in {'BIN_OP', 'UNARY_OP'}:
            # Do not obfuscate operators
            pass

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
        should_obf = identifier not in self.identifier_map and identifier not in self.reserved_keywords
        if should_obf:
            logging.debug(f"Identifier '{identifier}' is eligible for obfuscation.")
        else:
            logging.debug(f"Identifier '{identifier}' is NOT eligible for obfuscation.")
        return should_obf

    def _add_to_identifier_map(self, original_name, length=8):
        """
        Adds an identifier to the identifier map with a generated obfuscated name.

        Args:
            original_name (str): The original identifier name.
            length (int, optional): Length of the obfuscated name. Defaults to 8.
        """
        if original_name not in self.identifier_map:
            obfuscated_name = self._generate_random_name(length)
            while obfuscated_name in self.identifier_map.values():
                obfuscated_name = self._generate_random_name(length)
            self.identifier_map[original_name] = obfuscated_name
            logging.debug(f"Assigned obfuscated name '{obfuscated_name}' to identifier '{original_name}'.")

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
        logging.debug(f"Identifier map saved to {filepath}")

    def load_identifier_map(self, filepath='identifier_map.json'):
        """
        Loads the identifier map from a JSON file.

        Args:
            filepath (str, optional): Path to the JSON file. Defaults to 'identifier_map.json'.
        """
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.identifier_map = json.load(f)
            logging.debug(f"Identifier map loaded from {filepath}")
        else:
            logging.warning(f"No identifier map found at {filepath}")