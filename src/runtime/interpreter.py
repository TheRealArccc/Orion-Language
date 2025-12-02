from lexer import TokenType
from runtime.values_ import *
from tree import *
from runtime.environment import Environment
# from utils.errors import *

class Interpreter:
    def __init__(self):
        self.env = Environment()
        self.load_stdlib()

    def raise_error(self, message):
        raise Exception(message)

    def interpret(self, tree):
        if isinstance(tree, ProgramNode):
            self.visit(tree)

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit_{type(node).__name__} method defined")
    
    def visit_ProgramNode(self, node):
        result = None

        for statement in node.body:
            result = self.visit(statement)

        return result
    
    def visit_IndexAccessNode(self, node):
        arr = self.visit(node.array)
        index = self.visit(node.index).value
        if not isinstance(arr, list):
            self.raise_error("Cannot index non-list")
        if not isinstance(index, int):
            self.raise_error("Cannot index with non-integer")
        if abs(index) > len(arr):
            self.raise_error("Index is out of range")

        return arr[index]
    
    def visit_IndexAssignNode(self, node):
        arr = self.visit(node.array)
        index = self.visit(node.index).value
        value = self.visit(node.value)

        if not isinstance(arr, list):
            self.raise_error("Cannot index non-list")
        if not isinstance(index, int):
            self.raise_error("Cannot index with non-integer")
        if abs(index) > len(arr):
            self.raise_error("Index is out of range")

        arr[index] = value
        return value

    def visit_ArrayNode(self, node):
        return [self.visit(element) for element in node.elements]
    
    def visit_ReturnNode(self, node):
        raise ReturnSignal(self.visit(node.value))
    
    def visit_ParameterNode(self, node):
        return node.params.identifier

    def visit_FunctionDefNode(self, node):
        function = FunctionValue(node.name, node.params, node.body, self.env)
        self.env.declare(node.name, function)

    def visit_FunctionCallNode(self, node):
        func = self.env.get(node.name.value)

        # Evaluate arguments in the CURRENT environment (before switching)
        arg_values = [self.visit(arg) for arg in node.args]

        if isinstance(func, BuiltInFunctionValue):
            return func.call(self, arg_values)
        
        call_env = Environment(func.env)
        call_env.enter_scope()

        old_env = self.env
        self.env = call_env
        
        # Declare parameters with pre-evaluated argument values
        for param, arg_value in zip(func.params, arg_values):
            param_name = self.visit(param)
            call_env.declare(param_name, arg_value)
        
        try:
            for stmt in func.body:
                self.visit(stmt)
        except ReturnSignal as r:
            result = r.value
            call_env.exit_scope()
            self.env = old_env
            return result

        call_env.exit_scope()
        self.env = old_env
    
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
        identifier = node.identifier.identifier
        self.env.assign(identifier, value)

    def visit_VarDeclNode(self, node):
        value = self.visit(node.value)
        self.env.declare(node.identifier, value)

    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        op = node.op
        if op.value == '+':
            if isinstance(operand, IntValue):
                return IntValue(operand.value)
            elif isinstance(operand, FloatValue):
                return FloatValue(operand.value)
        elif op.value == '-':
            if isinstance(operand, IntValue):
                return IntValue(operand.value * -1)
            elif isinstance(operand, FloatValue):
                return FloatValue(operand.value * -1)

    def visit_BinaryOpNode(self, node):
        def eval_values(left, op, right):
            left = getattr(left, 'value', left)
            right = getattr(right, 'value', right)
            # Nothing value
            if op in ('+', '-', '*', '/') and None in (left, right):
                raise TypeError(f"Cannot perform operations with 'Nothing' type")
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return (str(left)+str(right))
                return (left+right)
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

        op = node.op
        left = self.visit(node.left)
        if op.type == TokenType.AND:
            if left == False:
                return False
            else:
                return self.visit(node.right)
        elif op.type == TokenType.OR:
            if left:
                return True
            else:
                return self.visit(node.right)
        right = self.visit(node.right)
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
        
    def load_stdlib(self):
        def builtin_print(interpreter, args):
            values = [getattr(arg, 'value', arg) for arg in args]
            print(*values)
            return NothingValue(None)
        
        def builtin_int(interpreter, args):
            if not args:
                raise Exception("int() needs 1 argument")
            elif len(args) > 1:
                raise Exception("int() only takes in 1 argument")
            return IntValue(int(getattr(args[0], 'value', args[0])))
        
        def builtin_float(interpreter, args):
            if not args:
                raise Exception("float() needs 1 argument")
            elif len(args) > 1:
                raise Exception("float() only takes in 1 argument")
            return FloatValue(float(getattr(args[0], 'value', args[0])))
        
        def builtin_string(interpreter, args):
            if not args:
                raise Exception("string() needs 1 argument")
            elif len(args) > 1:
                raise Exception("string() only takes in 1 argument")
            return StringValue(int(getattr(args[0], 'value', args[0])))
        
        def builtin_type(interpreter, args):
            if not args:
                raise Exception("string() needs 1 argument")
            elif len(args) > 1:
                raise Exception("string() only takes in 1 argument")
            return StringValue(int(getattr(args[0], 'value', args[0])))


        # def builtin_sqrt(interpreter, args):
        #     values = 
        
        self.env.declare("print", BuiltInFunctionValue("print", builtin_print))
        self.env.declare("int", BuiltInFunctionValue("int", builtin_int))
        self.env.declare("float", BuiltInFunctionValue("float", builtin_float))
        self.env.declare("string", BuiltInFunctionValue("string", builtin_string))