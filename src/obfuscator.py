import random
import string
from parser import ASTNode  # Added import for ASTNode

class Obfuscator:
    def __init__(self):
        self.identifier_map = {}
    
    def obfuscate(self, ast):
        self.rename_identifiers(ast)
        self.insert_dead_code(ast)
        return ast

    def rename_identifiers(self, node):
        if node.type == 'Identifier':
            if node.value not in self.identifier_map:
                obf_name = self.generate_random_name()
                self.identifier_map[node.value] = obf_name
            node.value = self.identifier_map[node.value]
        for child in node.children:
            self.rename_identifiers(child)

    def generate_random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    def insert_dead_code(self, node):
        # Example: Insert no-op statements
        if node.type == 'Program':
            dead_node = ASTNode('NoOp', children=[])
            node.children.insert(random.randint(0, len(node.children)), dead_node)
        for child in node.children:
            self.insert_dead_code(child)