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
        self.env.assign_var(identifier, value)
        print("SCOPE: ", self.env.scopes)

    def visit_VarDeclNode(self, node):
        value = self.visit(node.value)
        self.env.declare_var(node.identifier, value)
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
            if op == '+': return (left+right)
            elif op == '-':
                if right != 0: return (left-right) 
                else: raise ZeroDivisionError("Cannot divide by zero")
            elif op == '*': return (left*right)
            elif op == '/': return (left/right)
            elif op == '==': return bool(left==right)
            elif op == '>': return bool(left>right)
            elif op == '<': return bool(left<right)
            elif op == '<=': return bool(left<=right)
            elif op == '>=': return bool(left>=right)
            elif op == '!=': return bool(left!=right)
            elif op == '&&':
                if not left:
                    return False
                return bool(self.visit(right))
            elif op == '||':
                if left:
                    return True
                return bool(self.visit(right))

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
        value = self.env.get_var(identifier)
        return value
        
    def visit_NothingLiteralNode(self, node):
        token = node.literal
        if token == None:
            return NothingLiteralNode(token)
    
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