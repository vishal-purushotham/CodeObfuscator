class CodeGenerator:
    def __init__(self):
        pass

    def generate(self, ast):
        return self.generate_node(ast)

    def generate_node(self, node):
        method_name = f'gen_{node.type}'
        method = getattr(self, method_name, self.gen_default)
        return method(node)

    def gen_default(self, node):
        code = ""
        for child in node.children:
            code += self.generate_node(child)
        return code

    def gen_Program(self, node):
        code = ""
        for child in node.children:
            code += self.generate_node(child)
        return code

    def gen_FunctionDeclaration(self, node):
        return f"{self.generate_node(node.children[0])} {node.value}({self.generate_parameters(node.children[1])}) {{\n{self.generate_node(node.children[2])}}}\n\n"

    def generate_parameters(self, node):
        params = []
        for param in node.children:
            param_type = self.generate_node(param.children[0])
            param_name = param.value
            params.append(f"{param_type} {param_name}")
        return ", ".join(params)

    def gen_ReturnType(self, node):
        return node.value

    def gen_Type(self, node):
        return node.value

    def gen_Parameters(self, node):
        # Handled separately in gen_FunctionDeclaration
        return ""

    def gen_Body(self, node):
        code = ""
        for stmt in node.children:
            code += self.generate_node(stmt)
        return code

    def gen_Declaration(self, node):
        type_str = self.generate_node(node.children[0])
        var_name = node.value
        if len(node.children) > 1:
            assignment = self.generate_node(node.children[1])
            return f"{type_str} {var_name} = {assignment};\n"
        else:
            return f"{type_str} {var_name};\n"

    def gen_AssignmentStatement(self, node):
        var_name = node.value
        expr = self.generate_node(node.children[0])
        return f"{var_name} = {expr};\n"

    def gen_BIN_OP(self, node):
        left = self.generate_node(node.children[0])
        op = node.value
        right = self.generate_node(node.children[1])
        return f"{left} {op} {right}"

    def gen_Number(self, node):
        return f"{node.value}"

    def gen_String(self, node):
        return f"\"{node.value}\""

    def gen_Identifier(self, node):
        return f"{node.value}"

    def gen_UnaryOp(self, node):
        op = node.value
        operand = self.generate_node(node.children[0])
        return f"{op}{operand}"

    def gen_ReturnStatement(self, node):
        if node.children:
            expr = self.generate_node(node.children[0])
            return f"return {expr};\n"
        else:
            return "return;\n"

    def gen_IfStatement(self, node):
        condition = self.generate_node(node.children[0])
        then_branch = self.generate_node(node.children[1])
        code = f"if ({condition}) {{\n{then_branch}}}\n"
        if len(node.children) > 2:
            else_branch = self.generate_node(node.children[2])
            code += f"else {{\n{else_branch}}}\n"
        return code

    def gen_WhileStatement(self, node):
        condition = self.generate_node(node.children[0])
        body = self.generate_node(node.children[1])
        return f"while ({condition}) {{\n{body}}}\n"

    def gen_ForStatement(self, node):
        init = self.generate_node(node.children[0])
        condition = self.generate_node(node.children[1])
        increment = self.generate_node(node.children[2])
        body = self.generate_node(node.children[3])
        return f"for ({init} {condition}; {increment}) {{\n{body}}}\n"

    def gen_ExpressionStatement(self, node):
        expr = self.generate_node(node.children[0])
        return f"{expr};\n"

    def gen_PreprocessorDirective(self, node):
        return f"{node.value}\n"

    # Add more methods as needed for other AST node types