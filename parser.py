from dataclasses import dataclass
from lexer import TokenType, Token

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
class PostfixOpNode:
    identifier: str
    op: any

    def __repr__(self):
        return (f"({self.identifier.value}{self.op.value})")
    
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
        return (f"({self.identifier} = {self.value})")
    
@dataclass
class IfNode:
    condition: any
    body: any
    else_body: any = None

    def __repr__(self):
        return (f"(IF {self.condition} THEN \n\t{self.body} \n\tELSE {self.else_body})")

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
        if tokens:
            self.current_token = self.tokens[self.pos]

    def raise_error_expect(self, expected, got=None):
        if got == None:
            raise Exception(f"Expected '{expected}'")
        else:
            print(self.current_token)
            raise Exception(f"Expected '{expected}', got '{got}'")
        
    def raise_error(self, message):
        if message:
            raise Exception(str(message))
        else:
            raise Exception

    def advance(self):
        self.pos += 1
        if self.current_token and self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def peek(self):
        if self.pos + 1 < len(self.tokens) and self.pos + 1 != None:
            return self.tokens[self.pos + 1]
        return None
    
    def peek_prev_token(self):
        if self.pos - 1 > 0:
            return self.tokens[self.pos - 1]

    def parse(self):
        statements = []
        
        if self.tokens:
            while self.current_token != None:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
                
                # HANDLE SEMICOLONS/LINE ENDINGS
                if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                    self.advance()

        return ProgramNode(statements)

    def parse_statement(self):
        token = self.current_token

        if token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type == TokenType.EQUAL:
            return self.parse_assignment()
        if token.type == TokenType.VAR:
            return self.parse_var_decl()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        else:
            return self.parse_expr()
    
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
            self.raise_error_expect("identifier", self.current_token.type.name)
            
    ############### CONDITIONALS AND LOOPS #################
    def parse_if_statement(self):
        self.advance()
        print(f"IHHKHIH:{self.current_token}")
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            condition = self.parse_logical_or() ### <- FIX HERE

            if self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")", self.current_token.value)

            # BODY
            if self.current_token.type == TokenType.COLON:
                self.advance()
                body = []
                print(f"BODD: {body}")
                while self.current_token.type not in (TokenType.END, TokenType.ELSE):
                    stmt = self.parse_statement()
                    if stmt:
                        body.append(stmt)
                    # SEMICOLON
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    elif self.peek_prev_token() and self.peek_prev_token().type == TokenType.END:
                        continue
                    else:
                        self.raise_error_expect(";")
                print(self.current_token)
                        
                if self.current_token.type == TokenType.ELSE:
                    else_body = []
                    self.advance()
                    if self.current_token.type == TokenType.IF:
                        stmt = self.parse_if_statement()
                        if stmt:
                            else_body.append(stmt)
                    else:
                        if self.current_token.type == TokenType.COLON:
                            self.advance()
                            while self.current_token and self.current_token.type != TokenType.END:
                                stmt = self.parse_statement()
                                print(f"SJGF:?{self.current_token}")
                                if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                                    self.advance()
                                else:
                                    self.raise_error_expect(";")
                                if stmt:
                                    else_body.append(stmt)
                            if self.current_token and self.current_token.type == TokenType.END:
                                self.advance()
                                if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                                    self.advance()
                        else:
                            self.raise_error_expect(":")

                    if else_body == None:
                        self.raise_error("Expected content inside of else")
                    
                    return IfNode(condition, body, else_body)
                elif self.current_token.type == TokenType.END:
                    self.advance()
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    print(f"{condition}{body}")
                    return IfNode(condition=condition, body=body)
            else:
                self.raise_error_expect(expected=":", got=self.current_token)

    def parse_while_statement(self):
        self.advance()
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            condition = self.parse_logical_or()
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")")

            # BODY
            if self.current_token.type == TokenType.COLON:
                self.advance()
                body = []
                while self.current_token.type != TokenType.END:
                    stmt = self.parse_statement()
                    if stmt:
                        body.append(stmt)
                    if self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    else:
                        self.raise_error_expect(";")
                if self.current_token.type == TokenType.END:
                    self.advance()
                    return WhileNode(condition, body)
            else:
                self.raise_error_expect("end")
        else:
            self.raise_error_expect("(")

    def parse_for_statement(self):
        self.advance()
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.VAR:
                init = self.parse_var_decl()
                print(self.current_token)
                if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                    print("OKOKO")
                    self.advance()
                    condition = self.parse_logical_or()
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                        print(self.current_token)
                        # POST DECREMENT/INCREMENT
                        if self.current_token and self.current_token.type == TokenType.IDENTIFIER: 
                            postfixop_identifier = self.current_token
                            self.advance()
                            if self.current_token.type in (TokenType.MINUSMINUS, TokenType.PLUSPLUS):
                                postfixop_op = self.current_token
                                self.advance()

                                # RPAREN
                                if self.current_token and self.current_token.type == TokenType.RPAREN:
                                    self.advance()
                                    unopchange = PostfixOpNode(postfixop_identifier, postfixop_op)
                                else:
                                    self.raise_error_expect(")")
                            else:
                                self.raise_error_expect("++, --")
                        # PRE-DECREMENT/INCREMENT
                        elif self.current_token and self.current_token.type in (TokenType.MINUSMINUS, TokenType.PLUSPLUS): #Prefix Op
                            op = self.current_token
                            self.advance()
                            if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                                identifier = self.current_token
                                self.advance()
                                # RPAREN
                                if self.current_token and self.current_token.type == TokenType.RPAREN:
                                    self.advance()
                                    unopchange = AssignNode(identifier, BinaryOpNode(VariableNode(f"{identifier.value}"), Token(TokenType.PLUS, "+"), LiteralNode(Token(TokenType.INT, 1))))
                                else:
                                    self.raise_error_expect(")")
                            else:
                                self.raise_error(f"Expected identifier after '{op.value}'")
                        else:
                            self.raise_error("Expected increment or decrement")
                    else:
                        self.raise_error_expect(";")
                else:
                    self.raise_error_expect(";")
            else:
                self.raise_error_expect("var")
        else:
            self.raise_error_expect(")")
        
        # BODY
        if self.current_token.type == TokenType.COLON:
            self.advance()
            body = []
            while self.current_token != None and self.current_token.type not in (TokenType.END, None):
                stmt = self.parse_statement()
                if stmt:
                    body.append(stmt)
                if self.current_token.type == TokenType.SEMICOLON:
                    self.advance()
                elif self.peek_prev_token() and self.peek_prev_token().type == TokenType.END and self.current_token.type != TokenType.SEMICOLON:
                    continue                    
                else:
                    self.raise_error_expect(";")
                print(stmt)
            if body == []:
                self.raise_error("Body cannot be empty")
            if self.current_token and self.current_token.type == TokenType.END:
                self.advance()
            else:
                self.raise_error_expect("end")
        else:
            self.raise_error_expect(":")

        print(f"SSS{init}{condition}{unopchange}{body}")
        return ForNode(init, condition, unopchange, body)
    
    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.current_token != None and self.current_token.type == TokenType.OR:
            op = self.current_token
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode(left, op, right)
        return left
    
    def parse_logical_and(self):
        left = self.parse_condition()
        while self.current_token != None and self.current_token.type == TokenType.AND:
        
            op = self.current_token
            print(f"op:: {op}")
            self.advance()
            right = self.parse_condition()
            left = BinaryOpNode(left, op, right)
        return left
    
    def parse_condition(self):
        left = self.parse_expr()
        while self.current_token != None and self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.EQEQ, TokenType.LTEQ, TokenType.GTEQ, TokenType.NOTEQ):
            op = self.current_token
            self.advance()
            right = self.parse_expr()
            left = BinaryOpNode(left, op, right)
        if self.current_token.type == TokenType.EQUAL:
            print(self.current_token)
            self.raise_error("Unexpected operator")
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
        elif token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL):
            self.advance()
            return LiteralNode(token)
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(token.value)