from lexer import TokenType
from runtime.values_ import *
from tree import *
from runtime.environment import Environment
# from utils.errors import *

class Interpreter:
    def __init__(self):
        self.env = Environment()

    def interpret(self, tree):
        if isinstance(tree, ProgramNode):
            self.visit(tree)

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        print(method_name)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")
    
    def visit_ProgramNode(self, node):
        result = None

        for statement in node.body:
            result = self.visit(statement)

        return result
    
    def visit_ReturnNode(self, node):
        raise ReturnSignal(self.visit(node.value))
    
    def visit_ParameterNode(self, node):
        print(node.params.value)
        return node.params.value

    def visit_FunctionDefNode(self, node):
        function = FunctionValue(node.name, node.params, node.body, self.env)
        self.env.declare(node.name, function)

    def visit_FunctionCallNode(self, node):
        func = self.env.get(node.name.value)

        call_env = Environment(func.env)
        call_env.enter_scope()

        old_env = self.env
        self.env = call_env
        for param, arg in zip(func.params, node.args):
            call_env.declare(self.visit(param), self.visit(arg))
        
        try:
            for stmt in func.body:
                self.visit(stmt)
        except ReturnSignal as r:
            result = r.value
            return r

        call_env.exit_scope()
        self.env = old_env

        print(func)
        print(self.env.scopes)
    
    def visit_WhileNode(self, node):
        self.env.enter_scope()
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
        self.env.exit_scope()
        print(self.env.scopes)
    
    def visit_ForNode(self, node):
        self.env.enter_scope()
        self.visit(node.init)
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)
            
            self.visit(node.increment)
        self.env.exit_scope()
        print(self.env.scopes)

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        if condition:
            self.env.enter_scope()
            for stmt in node.body:
                self.visit(stmt)
            self.env.exit_scope()
        elif node.else_body:
            self.env.enter_scope()
            for stmt in node.else_body:
                self.visit(stmt)
            self.env.exit_scope()
    
    def visit_AssignNode(self, node):
        value = self.visit(node.value)
        identifier = node.identifier
        self.env.assign(identifier, value)
        print("SCOPE: ", self.env.scopes)

    def visit_VarDeclNode(self, node):
        value = self.visit(node.value)
        self.env.declare(node.identifier, value)
        print("SCOPE: ", self.env.scopes)

    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        op = node.op
        if op.value == '+':
            if node.operand.literal.type == TokenType.INT:
                return IntValue(operand.value)
            elif node.operand.literal.type == TokenType.FLOAT:
                return FloatValue(operand.value)
        elif op.value == '-':
            if node.operand.literal.type == TokenType.INT:
                return IntValue(operand.value * -1)
            elif node.operand.literal.type == TokenType.FLOAT:
                return FloatValue(operand.value * -1)

    def visit_BinaryOpNode(self, node):
        def eval_values(left, op, right):
            left = getattr(left, 'value', left)
            right = getattr(right, 'value', right)
            # Nothing value
            if op in ('+', '-', '*', '/') and None in (left, right):
                print(left)
                raise TypeError(f"Cannot perform operations with 'Nothing' type")
            if op == '+': return (left+right)
            elif op == '-': return (left-right)
            elif op == '*': return (left*right)
            elif op == '/':
                if right != 0: return (left/right) 
                else: raise ZeroDivisionError("Cannot divide by zero")
            elif op == '==': return bool(left==right)
            elif op == '>': return bool(left>right)
            elif op == '<': return bool(left<right)
            elif op == '<=': return bool(left<=right)
            elif op == '>=': return bool(left>=right)
            elif op == '!=': return bool(left!=right)
            elif op == '&&':
                if left == False:
                    return False
                return bool(right)
            elif op == '||':
                if right == True:
                    return right
                return bool(left)

        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op
        if op.type == TokenType.PLUS:
            return eval_values(left, '+', right)
        elif op.type == TokenType.MINUS:
            return eval_values(left, '-', right)
        elif op.type == TokenType.MUL:
            return eval_values(left, '*', right)
        elif op.type == TokenType.DIV:
            return eval_values(left, '/', right)
        # BOOLEAN OPS
        elif op.type == TokenType.EQEQ:
            return eval_values(left, '==', right)
        elif op.type == TokenType.GT:
            return eval_values(left, '>', right)
        elif op.type == TokenType.LT:
            return eval_values(left, '<', right)
        elif op.type == TokenType.LTEQ:
            return eval_values(left, '<=', right)
        elif op.type == TokenType.GTEQ:
            return eval_values(left, '>=', right)
        elif op.type == TokenType.NOTEQ:
            return eval_values(left, '!=', right)
        elif op.type == TokenType.AND:
            return eval_values(left, '&&', right)
        elif op.type == TokenType.OR:
            return eval_values(left, '||', right)
        
    def visit_VariableNode(self, node):
        identifier = node.identifier
        value = self.env.get(identifier)
        return value
    
    def visit_PostfixOpNode(self, node):
        identifier = node.identifier
        value = self.env.get(identifier)
        if node.op.type == TokenType.PLUSPLUS:
            old_value = value
            value.value += 1
            self.env.assign(identifier, value)
        if node.op.type == TokenType.MINUSMINUS:
            old_value = value
            value.value -= 1
            self.env.assign(identifier, value)
        return old_value
        
    def visit_NothingLiteralNode(self, node):
        token = node.literal
        if token == None:
            return NothingValue(token)
    
    def visit_LiteralNode(self, node):
        token = node.literal
        if token.type == TokenType.INT:
            return IntValue(token.value)
        elif token.type == TokenType.FLOAT:
            return FloatValue(token.value)
        elif token.type == TokenType.STRING:
            return StringValue(token.value)
        elif token.type == TokenType.BOOL:
            return BoolValue(token.value)