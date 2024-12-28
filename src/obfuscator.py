import string
import random


class Obfuscator:
    def __init__(self):
        self.identifier_map = {}

    def obfuscate(self, ast):
        self._obfuscate_node(ast)
        return ast

    def _obfuscate_node(self, node):
        # Rename identifiers used in variable declarations
        if node.type == 'Declaration' or node.type == 'AssignmentStatement':
            original_name = node.value
            if original_name not in self.identifier_map:
                self.identifier_map[original_name] = self._generate_random_name()
            node.value = self.identifier_map[original_name]

        # Rename identifiers used elsewhere (e.g., in expressions)
        elif node.type == 'Identifier':
            original_name = node.value
            if original_name in self.identifier_map:
                node.value = self.identifier_map[original_name]

        for child in node.children:
            if child:
                self._obfuscate_node(child)

    def _generate_random_name(self, length=8):
        letters = string.ascii_letters
        # Ensure the first character is a letter or underscore
        first_char = random.choice(string.ascii_letters + "_")
        other_chars = ''.join(random.choice(letters + string.digits + "_") for _ in range(length - 1))
        return first_char + other_chars