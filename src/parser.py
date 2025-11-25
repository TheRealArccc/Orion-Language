from lexer import TokenType, Token
from tree import *

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
            raise Exception(f"Expected '{expected}', got '{got.value}'")
        
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
        if self.pos - 1 >= 0:
            return self.tokens[self.pos - 1]
        return None

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
                elif self.peek_prev_token() and self.peek_prev_token().type == TokenType.END:
                    continue
                else:
                    self.raise_error_expect(';', self.current_token)

        return ProgramNode(statements)

    def parse_statement(self):
        token = self.current_token

        if token.type == TokenType.IDENTIFIER and self.peek():
            return self.parse_identifier()
        if token.type == TokenType.VAR:
            return self.parse_var_decl()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif token.type == TokenType.FUNC:
            return self.parse_function_def()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            # if token and token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.MUL, TokenType.DIV, TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.RPAREN):
            #     return self.parse_expr()
            return self.raise_error(f"Unexpected token: {token}")
        
    def parse_identifier(self):
        peek = self.peek()
        print(peek)
        if peek != None and peek.type == TokenType.EQUAL:
            return self.parse_assignment()
        elif peek != None and peek.type == TokenType.LPAREN:
            return self.parse_function_call()
        else:
            self.raise_error(f"Invalid token after: {self.current_token}")
    
    def parse_assignment(self):
        identifier = self.current_token
        self.advance()
        if self.current_token.type ==TokenType.EQUAL:
            self.advance()
            return AssignNode(identifier.value, self.parse_expr())

    def parse_var_decl(self):
        self.advance()
        if self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()

            if self.current_token.type == TokenType.EQUAL:
                self.advance()
                value = self.parse_expr()
                if value:
                    return VarDeclNode(identifier, value)
                self.raise_error(f"'{identifier}' must have a declared value")
            else:
                self.raise_error_expect("=", self.current_token)
        else:
            self.raise_error_expect("identifier", self.current_token)

    def parse_return_statement(self):
        self.advance()
        if self.current_token and self.current_token.type in (TokenType.SEMICOLON, TokenType.NOTHING):
            self.advance()
            return ReturnNode(NothingLiteralNode(None))
        value = self.parse_expr()
        return ReturnNode(value)

    # FUNCTIONS
    def parse_function_call(self):
        name = self.current_token
        self.advance()
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            args = self.parse_arguments()
            if args and args == "error":
                self.raise_error(f"Unexpected argument error for method '{name.value}()'")
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
                return FunctionCallNode(name, args)
            else:
                self.raise_error_expect(")", self.current_token)
        else:
            self.raise_error_expect("(", self.current_token)

    def parse_arguments(self):
        if self.current_token and self.peek_prev_token() and self.peek_prev_token().type == TokenType.LPAREN:
            try:
                args = []
                if self.current_token and self.current_token.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.INT, TokenType.FLOAT, TokenType.BOOL):
                    args.append(self.parse_expr())
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        if self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()
                            if self.current_token and self.current_token.type not in (TokenType.IDENTIFIER, TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL, TokenType.NOTHING):
                               return "error"
                        if self.current_token and self.current_token.type != TokenType.COMMA:
                            args.append(self.parse_expr())
                return args
            except Exception:
                return "error"
        else:
            self.raise_error_expect("(", self.current_token)

    def parse_function_def(self):
        self.advance()
        name = None
        params = []
        body = []
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    params = self.parse_parameters()
                
                if params and params == "error":
                    self.raise_error(f"Unexpected parameter error for function '{name.value}()'")
                if self.current_token and self.current_token.type == TokenType.RPAREN:
                    self.advance()
                else:
                    self.raise_error_expect(")", self.current_token)

                if self.current_token and self.current_token.type == TokenType.COLON:
                    self.advance()
                    while self.current_token and self.current_token.type != TokenType.END:
                        stmt = self.parse_statement()
                        if stmt:
                            body.append(stmt)
                        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                            self.advance()
                        elif self.peek_prev_token() and self.peek_prev_token().type == TokenType.END:
                            continue
                        elif self.current_token and self.current_token.type == TokenType.END:
                            break
                        else:
                            self.raise_error_expect(";", self.current_token)
                    if self.current_token and self.current_token.type == TokenType.END:
                        self.advance()
                    else:
                        self.raise_error_expect("end", self.current_token)
                else:
                    self.raise_error_expect(":", self.current_token)
            else:
                self.raise_error_expect("(", self.current_token)
        else:
            self.raise_error("Expected function identifier")

        return FunctionDefNode(name, params, body)
    
    def parse_parameters(self):
        if self.current_token and self.peek_prev_token() and self.peek_prev_token().type == TokenType.LPAREN:
            try:
                params = []
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    params.append(ParameterNode(self.parse_expr()))
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        if self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()
                        if self.current_token and self.current_token.type != TokenType.COMMA:
                            params.append(ParameterNode(self.parse_expr()))
                return params
            except Exception:
                return "error"
        else:
            self.raise_error_expect("(", self.current_token)
            
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
                    start_pos = self.pos
                    stmt = self.parse_statement()
                    if stmt:
                        body.append(stmt)
                    if start_pos == self.pos:
                        self.raise_error("Parser did not advance in if statement")
                    # SEMICOLON
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    elif self.current_token and self.current_token.type == TokenType.END:
                        break
                    elif self.peek_prev_token() and self.peek_prev_token().type == TokenType.END:
                        continue
                    else:
                        self.raise_error_expect(";")
                print(self.current_token)
                        
                if self.current_token and self.current_token.type == TokenType.ELSE:
                    else_body = []
                    self.advance()
                    if self.current_token and self.current_token.type == TokenType.IF:
                        stmt = self.parse_if_statement()
                        if stmt:
                            else_body.append(stmt)
                    else:
                        if self.current_token and self.current_token.type == TokenType.COLON:
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

                    if else_body == []:
                        self.raise_error("Expected content inside of else")
                    
                    return IfNode(condition, body, else_body)
                elif self.current_token and self.current_token.type == TokenType.END:
                    print("N"*20)
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
                while self.current_token and self.current_token.type != TokenType.END:
                    stmt = self.parse_statement()
                    if stmt:
                        body.append(stmt)
                    if self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
                    else:
                        self.raise_error_expect(";")
                if self.current_token and self.current_token.type == TokenType.END:
                    self.advance()
                    return WhileNode(condition, body)
                else:
                    self.raise_error_expect("end")
            else:
                self.raise_error_expect(":")
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
                                    unopchange = PostfixOpNode(postfixop_identifier.value, postfixop_op)
                                else:
                                    self.raise_error_expect(")", self.current_token)
                            elif self.current_token and self.current_token.type == TokenType.EQUAL:
                                self.advance()
                                unopchange = AssignNode(postfixop_identifier.value, self.parse_expr())
                                if self.current_token and self.current_token.type == TokenType.RPAREN:
                                    self.advance()
                                else:
                                    self.raise_error_expect(")", self.current_token)
                            else:
                                self.raise_error("Expected assignment in for statement")
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
                                    unopchange = AssignNode(identifier.value, BinaryOpNode(VariableNode(f"{identifier.value}"), Token(TokenType.PLUS, "+"), LiteralNode(Token(TokenType.INT, 1))))
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
            if self.peek() and self.peek().type == TokenType.LPAREN:
                return self.parse_function_call()
            self.advance()
            return VariableNode(token.value)
        elif token.type == TokenType.NOTHING:
            self.advance()
            return NothingLiteralNode(None)