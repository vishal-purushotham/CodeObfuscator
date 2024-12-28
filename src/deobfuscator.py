class Deobfuscator:
    def __init__(self, identifier_map):
        self.identifier_map = identifier_map
    
    def deobfuscate(self, ast):
        self.restore_identifiers(ast)
        self.remove_dead_code(ast)
        return ast
    
    def restore_identifiers(self, node):
        if node.type == 'Identifier':
            original = self.get_original_name(node.value)
            if original:
                node.value = original
        for child in node.children:
            self.restore_identifiers(child)
    
    def get_original_name(self, obf_name):
        for key, value in self.identifier_map.items():
            if value == obf_name:
                return key
        return obf_name
    
    def remove_dead_code(self, node):
        if node.type == 'Program':
            node.children = [child for child in node.children if child.type != 'NoOp']
        for child in node.children:
            self.remove_dead_code(child)