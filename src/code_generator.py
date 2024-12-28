class CodeGenerator:
    def generate(self, ast):
        return self.visit(ast)
    
    def visit(self, node):
        method_name = f'visit_{node.type}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        code = ''
        for child in node.children:
            code += self.visit(child)
        return code
    
    def visit_Program(self, node):
        code = ''
        for child in node.children:
            code += self.visit(child) + '\n'
        return code
    
    def visit_Declaration(self, node):
        type_node = node.children[0]
        return f"{type_node.value} {node.value};"
    
    def visit_Assignment(self, node):
        expr = self.visit(node.children[0])
        return f"{node.value} = {expr};"
    
    def visit_BinOp(self, node):
        left = self.visit(node.children[0])
        right = self.visit(node.children[1])
        return f"({left} {node.value} {right})"
    
    def visit_UnaryOp(self, node):
        operand = self.visit(node.children[0])
        return f"({node.value}{operand})"
    
    def visit_Number(self, node):
        return str(node.value)
    
    def visit_String(self, node):
        return f"\"{node.value}\""
    
    def visit_Identifier(self, node):
        return node.value
    
    def visit_If(self, node):
        condition = self.visit(node.children[0])
        then_branch = self.visit(node.children[1])
        return f"if ({condition}) {{\n{then_branch}\n}}"
    
    def visit_Then(self, node):
        code = ''
        for child in node.children:
            code += self.visit(child) + '\n'
        return code
    
    def visit_While(self, node):
        condition = self.visit(node.children[0])
        body = self.visit(node.children[1])
        return f"while ({condition}) {{\n{body}\n}}"
    
    def visit_Body(self, node):
        code = ''
        for child in node.children:
            code += self.visit(child) + '\n'
        return code
    
    def visit_NoOp(self, node):
        return "// Dead code inserted for obfuscation"