# FIXED IF NESTING
# FIXED parse_if_statement()

from dataclasses import dataclass
from lexer import TokenType

@dataclass
class ProgramNode:
    body: any

    def __repr__(self):
        return (f"PROGRAM({self.body})")

@dataclass
class BinaryOpNode:
    left: any
    op: any
    right: any
    

    def __repr__(self):
        return (f"({self.left} {self.op.value} {self.right})")

@dataclass
class LiteralNode:
    literal: any

    def __repr__(self):
        return str(self.literal.value)
    
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
    value: any = None

    def __repr__(self):
        return (f"(var {self.identifier} = {self.value})")
    
@dataclass
class AssignNode:
    identifier: any
    value: any

    def __repr__(self):
        return (f"({self.identifier.value} = {self.value})")
    
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
        self.tokens = tokens or []
        self.pos = 0
        self.current_token = self.tokens[self.pos]

    def raise_error_expect(self, expected, got=None):
        if got == None:
            raise Exception(f"Excpected '{expected}'")
        else:
            raise Exception(f"Expected '{expected}', got '{got}'")
        
    def raise_error(self, message):
        if message:
            raise Exception(str(message))
        else:
            return

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens) and self.current_token != None:
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None
    
    def peek_prev_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos + 1]

    def parse(self):
        statements = []
        
        while self.current_token != None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            
            # HANDLE SEMICOLONS/LINE ENDINGS
            if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                self.advance()

        return ProgramNode(statements)

    ########### FIX MULTI-STATEMENT PARSING ############ 
    def parse_statement(self, current_statement=None):
        token = self.current_token

        if token.type == TokenType.IDENTIFIER:
            if current_statement == None:
                return self.parse_assignment()
            return (f"{current_statement}{self.parse_assignment()}")
        if token.type == TokenType.VAR:
            if current_statement == None:
                return self.parse_var_decl()
            return (f"{current_statement}{self.parse_var_decl()}")
        elif token.type == TokenType.IF:
            if current_statement == None:
                return self.parse_if_statement()
            return (f"{current_statement}{self.parse_if_statement()}")
        # elif token.type == TokenType.WHILE:
        #     return self.parse_while_statement()
        else:
            if current_statement == None:
                return self.parse_expr()
            return {f"{current_statement}{self.parse_expr()}"}
        
    def parse_logical_or(self, left):
        op = self.current_token
        self.advance()
        right = self.parse_condition()
        self.advance()
        return BinaryOpNode(left, op, right)

    def parse_logical_and(self, left):
        op = self.current_token
        self.advance()
        right = self.parse_condition()
        self.advance()
        return BinaryOpNode(left, op, right)
    
    def parse_assignment(self):
        identifier = self.current_token
        self.advance()
        if self.current_token.type ==TokenType.EQUAL:
            self.advance()
            return AssignNode(identifier, self.parse_expr())

    def parse_var_decl(self):
        self.advance()
        if self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()

            if self.current_token.type == TokenType.EQUAL:
                self.advance()
                
                return VarDeclNode(identifier, self.parse_expr())
            else:
                self.raise_error_expect("=", self.current_token.value)
        else:
            self.raise_error_expect("IDENTIFIER", self.current_token.type.name)
            
    def parse_if_statement(self):
        self.advance()
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            condition = self.parse_condition() ### <- FIX HERE
            # AND/OR
            if self.current_token.type == TokenType.AND:
                condition = self.parse_logical_and(condition)
            elif self.current_token.type == TokenType.OR:
                condition = self.parse_logical_or(condition)
            elif self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")", self.current_token.value)
            # BODY
            if self.current_token.type == TokenType.COLON:
                self.advance()
                body = self.parse_statement()
                if self.peek() != None:
                    self.advance()
                while self.current_token.type not in (TokenType.END, TokenType.ELSE):
                    body = self.parse_statement(body)
                    # SEMICOLON
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    else:
                        self.raise_error_expect(";")
                        
                if self.current_token.type == TokenType.ELSE:
                    else_body = None
                    self.advance()
                    if self.current_token.type == TokenType.IF:
                        print("ELSE IF")
                        else_body = self.parse_if_statement()
                        print(else_body)
                    else:
                        if self.current_token.type == TokenType.COLON:
                            self.advance()
                            while self.current_token.type != TokenType.END:
                                else_body = self.parse_statement()
                                self.advance()
                        else:
                            self.raise_error_expect(":")

                    if else_body == None:
                        self.raise_error("Unexpected error")
                    
                    return IfNode(condition, body, else_body)
                elif self.current_token.type == TokenType.END:
                    self.advance()
                    print(f"{condition}{body}")
                    return IfNode(condition=condition, body=body)
            else:
                self.raise_error_expect(expected=":", got=self.current_token)

    def parse_condition(self):
        left = self.parse_expr()
        while self.current_token != None and self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.EQEQ, TokenType.LTEQ, TokenType.GTEQ, TokenType.NOTEQ):
            op = self.current_token
            self.advance()
            right = self.parse_expr()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_expr(self):
        left = self.parse_term()

        while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS): 
            op = self.current_token
            self.advance()
            right = self.parse_term()
            left = BinaryOpNode(left, op, right)
        return left
    
    def parse_term(self):
        left = self.parse_factor()
        while self.current_token != None and self.current_token.type in (TokenType.MUL, TokenType.DIV):
            op = self.current_token
            self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right)
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
                return expr
            else:
                self.raise_error_expect(")", self.current_token)
        elif token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL, TokenType.IDENTIFIER):
            self.advance()
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