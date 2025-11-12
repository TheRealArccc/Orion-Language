from dataclasses import dataclass
from lexer import TokenType

@dataclass
class ProgramNode:
    body: any

    def __repr__(self):
        return ("f({self.body})")

@dataclass
class BinaryOpNode:
    left: any
    right: any
    op: any

    def __repr__(self):
        return (f"({self.left}, {self.op.value}, {self.right})")

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
        return (f"(var {self.identifier} = {self.value})")
    
@dataclass
class AssignNode:
    identifier: any
    value = any

    def __repr__(self):
        return (f"({self.identifier} = {self.value})")
    
@dataclass
class IfNode:
    condition: any
    body: any
    else_body: any = None

    def __repr__(self):
        return (f"(IF {self.condition} THEN {self.body} ELSE {self.else_body})")

@dataclass
class WhileNode:
    condition: any
    body: any

    def __repr__(self):
        return (f"(WHILE {self.condition} DO {self.body})")

@dataclass
class ForNode:
    init: any
    condition: any
    increment: any
    body: any

    def __repr__(self):
        return (f"(FOR {self.init}; {self.condition}; {self.increment} DO {self.body})")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.advance()

    def raise_error_expect(self, expected, got):
        raise Exception(f"Expected '{expected}', got '{got}'")
        

    def advance(self):
        if self.pos < len(self.tokens) and self.current_token != None:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token == None

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def parse(self):
        statements = []

        while self.current_token != None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            # HANDLE SEMICOLONS/LINE ENDINGS

        return ProgramNode(statements)

    def parse_statement(self):
        token = self.current_token

        if token.type == TokenType.VAR:
            return self.parse_var_decl()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        # elif token.type == TokenType.WHILE:
        #     return self.parse_while_statement()
        else:
            return self.parse_expr()
        
    def parse_var_decl(self):
        if (self.peek()).type == TokenType.IDENTIFIER:
            self.advance()
            identifier = self.current_token.value

            if (self.peek()).type == TokenType.EQUAL:
                self.advance()
                return VarDeclNode(identifier, self.parse_expr())
            
    def parse_if_statement(self):
        if (self.peek()).type == TokenType.LPAREN:
            self.advance()
            self.advance()
            
            condition = self.parse_expr()
            while self.current_token.type != TokenType.RPAREN:
                self.advance()
                condition.append(self.parse_statement())

            self.advance()
            if self.current_token.type == TokenType.COLON:
                self.advance()

                body = []
                while self.current_token.type not in (TokenType.END, TokenType.ELSE):
                    body.append(self.parse_statement())

                else_body = []
                if self.current_token.type == TokenType.ELSE:
                    self.advance()
                    if self.current_token.type == TokenType.IF:
                        self.parse_if_statement()
                    
                    while self.current_token != TokenType.END:
                        else_body.append(self.parse_expr)
                
                return IfNode(condition, body, else_body)
            else:
                self.raise_error_expect(expected=":", got=self.current_token)

    def parse_expr(self):
        left = self.parse_term()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.advance()
            right = self.parse_term()
            left = BinaryOpNode(left, right, op)
        return left
    
    def parse_term(self):
        left = self.parse_factor()

        while self.current_token != None and self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, right, op)
        return left
    
    def parse_factor(self):
        token = self.current_token

        if token.type in (TokenType.PLUS, TokenType.MINUS):
            self.advance()
            op = token
            operand = self.parse_factor()
            return UnaryOpNode(op, operand)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            if self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")", self.current_token)
        elif token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL, TokenType.IDENTIFIER):
            return LiteralNode(token)
        












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