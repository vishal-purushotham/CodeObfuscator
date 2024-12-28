class Deobfuscator:
    def __init__(self, identifier_map):
        # Create a reverse mapping for deobfuscation
        self.reverse_map = {v: k for k, v in identifier_map.items()}

    def deobfuscate(self, ast):
        self._deobfuscate_node(ast)
        return ast

    def _deobfuscate_node(self, node):
        # Revert obfuscated names in declarations and assignments
        if node.type == 'Declaration' or node.type == 'AssignmentStatement':
            obf_name = node.value
            if obf_name in self.reverse_map:
                node.value = self.reverse_map[obf_name]

        # Revert obfuscated names in identifier usages
        elif node.type == 'Identifier':
            obf_name = node.value
            if obf_name in self.reverse_map:
                node.value = self.reverse_map[obf_name]

        for child in node.children:
            if child:
                self._deobfuscate_node(child)