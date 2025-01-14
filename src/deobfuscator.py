# src/deobfuscator.py

class Deobfuscator:
    def __init__(self, identifier_map):
        """
        Initializes the Deobfuscator with a reverse mapping.

        Args:
            identifier_map (dict): A dictionary mapping original identifiers to obfuscated names.
        """
        # Create a reverse mapping: obfuscated_name -> original_name
        self.reverse_map = {v: k for k, v in identifier_map.items()}
        print("Reverse Identifier Map:", self.reverse_map)  # Debugging Statement

    def deobfuscate(self, ast):
        """
        Starts the deobfuscation process by traversing the AST.

        Args:
            ast (ASTNode): The root of the Abstract Syntax Tree.

        Returns:
            ASTNode: The deobfuscated AST.
        """
        self._deobfuscate_node(ast)
        return ast

    def _deobfuscate_node(self, node):
        """
        Recursively traverses the AST and replaces obfuscated identifiers.

        Args:
            node (ASTNode): The current AST node.
        """
        # Check if the current node contains an identifier to deobfuscate
        if hasattr(node, 'value') and node.value in self.reverse_map:
            original_name = self.reverse_map[node.value]
            print(f"Deobfuscating '{node.value}' to '{original_name}'")  # Debugging Statement
            node.value = original_name

        # If the node has children, traverse them recursively
        for child in getattr(node, 'children', []):
            if child:
                self._deobfuscate_node(child)