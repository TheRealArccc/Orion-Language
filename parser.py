from dataclasses import dataclass
from lexer import TokenType

@dataclass
class ProgramNode:
    body: any

    def __repr__(self):
        return (f"{self.__class__.__name__}({self.body})")

@dataclass
class BinaryOpNode:
    left: any
    right: any
    op: any

    def __repr__(self):
        return (f"{self.__class__.__name__}({self.left}, {self.op.value}, {self.right})")

@dataclass
class LiteralNode:
    literal: any

    def __repr__(self):
        return self.literal.value
    
@dataclass
class UnaryOpNode:
    op: any
    operand: any

    def __repr__(self):
        return (f"{self.op.value}{self.operand}")
    
@dataclass
class VariableNode:
    identifier: any

    def __repr__(self):
        return self.identifier
    
@dataclass
class VarDeclNode:
    identifier: any
    value = any

    def __repr__(self):
        return (f"{self.__class__.__name__}(var {self.identifier} = {self.value})")
    
@dataclass
class AssignNode:
    identifier: any
    value = any

    def __repr__(self):
        return (f"{self.__class__.__name__}({self.identifier} = {self.value})")
    
@dataclass
class IfNode:
    condition: any
    body: any
    else_body: any = None

    def __repr__(self):
        return (f"{self.__class__.__name__}(IF {self.condition} THEN {self.body} ELSE {self.else_body})")

@dataclass
class WhileNode:
    condition: any
    body: any

    def __repr__(self):
        return (f"{self.__class__.__name__}(WHILE {self.condition} DO {self.body})")

@dataclass
class ForNode:
    init: any
    condition: any
    increment: any
    body: any

    def __repr__(self):
        return (f"{self.__class__.__name__}(FOR {self.init}; {self.condition}; {self.increment} DO {self.body})")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens(self.pos)
        self.advance()

    def raise_error_expect(self):
        

    def advance(self):
        if self.pos < len(self.tokens) and self.current_token != None:
            pos += 1
            self.current_token = self.tokens(self.pos)
        else:
            self.current_token == None

    def parse(self):
        result = self.

    def parse_statement(self):

    def comparison(self):

    def expr(self):

    def term(self):
    
    def factor(self):


























# class Parser:
#     def __init__(self, tokens):
#         self.tokens = tokens
#         self.pos = 0        # current token position
#         self.current_token = tokens[self.pos]

#     # ---- Utility Functions ----
#     def advance(self):
#         self.pos += 1
#         if self.pos < len(self.tokens):
#             self.current_token = self.tokens[self.pos]
#         else:
#             self.current_token = None

#     def expect(self, token_type):
#         # Raise error if current_token is not token_type
#         pass

#     # ---- Parser Entry Point ----
#     def parse_program(self):
#         """
#         Program → Statement*
#         Returns a ProgramNode containing a list of statements.
#         """
#         statements = []
#         while self.current_token is not None:
#             statements.append(self.parse_statement())
#         return ProgramNode(statements)

#     # ---- Statements ----
#     def parse_statement(self):
#         if self.current_token.type == TokenType.IDENTIFIER:
#             return self.parse_assignment_or_call()
#         elif self.current_token.type == TokenType.IF:
#             return self.parse_if_statement()
#         elif self.current_token.type == TokenType.WHILE:
#             return self.parse_while_statement()
#         elif self.current_token.type == TokenType.FOR:
#             return self.parse_for_statement()
#         elif self.current_token.type == TokenType.RETURN:
#             return self.parse_return_statement()
#         else:
#             raise Exception("Unexpected token in statement")

#     # ---- Expressions ----
#     def parse_expression(self):
#         """
#         Handles binary expressions, comparisons, boolean logic.
#         Returns an ExpressionNode.
#         """
#         # Could call parse_term() / parse_factor() recursively
#         pass

#     def parse_term(self):
#         pass

#     def parse_factor(self):
#         pass

#     # ---- Control Flow Blocks ----
#     def parse_if_statement(self):
#         """
#         IF → '(' Expression ')' ':' StatementList (ELSE ':' StatementList)? END
#         """
#         pass

#     def parse_while_statement(self):
#         pass

#     def parse_for_statement(self):
#         pass

#     # ---- Misc ----
#     def parse_assignment_or_call(self):
#         pass

#     def parse_return_statement(self):
#         pass