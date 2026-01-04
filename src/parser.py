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
    
    def peek_prev_token(self, count=1):
        if self.pos - 1 >= 0:
            return self.tokens[self.pos - count]
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
        elif token.type == TokenType.ARRAY:
            return self.parse_array_decl()
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
        elif token.type == TokenType.IMPORT:
            return self.parse_import_statement()
        else:
            # if token and token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.MUL, TokenType.DIV, TokenType.PLUS, TokenType.MINUS, TokenType.LPAREN, TokenType.RPAREN):
            #     return self.parse_expr()
            return self.raise_error(f"Unexpected token: {token.value}")
        
    def parse_identifier(self):
        peek = self.peek()
        if peek != None and peek.type in (TokenType.EQUAL, TokenType.LBRACKET):
            return self.parse_assignment()
        elif peek != None and peek.type == TokenType.LPAREN:
            return self.parse_function_call()
        elif peek != None and peek.type == TokenType.DOT:
            return self.parse_method_call()
        else:
            self.raise_error(f"Invalid token after: {self.current_token}")
    
    def parse_assignment(self):
        identifier = self.parse_index_access()
        if self.current_token.type == TokenType.EQUAL:
            self.advance()
            if isinstance(identifier, IndexAccessNode):
                return IndexAssignNode(identifier.array, identifier.index, self.parse_expr())
            return AssignNode(getattr(identifier, 'value', identifier), self.parse_expr())

    def parse_var_decl(self):
        self.advance()
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()

            if self.current_token and self.current_token.type == TokenType.EQUAL:
                self.advance()
                value = self.parse_expr()
                if value:
                    return VarDeclNode(identifier, value)
                self.raise_error(f"'{identifier}' must have a declared value")
            else:
                self.raise_error_expect("=", self.current_token)
        else:
            self.raise_error_expect("identifier", self.current_token)

    def parse_array(self):
        elements = []
        self.advance()
        if self.current_token and self.current_token.type != TokenType.RBRACKET:
            stmt = self.parse_expr()
            if stmt:
                elements.append(stmt)
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                stmt = self.parse_expr()
                if stmt:
                    elements.append(stmt)
            if self.current_token and self.current_token.type == TokenType.RBRACKET:
                self.advance()
                return elements
            else:
                self.raise_error_expect("]", self.current_token)

    def parse_array_decl(self):
        self.advance()
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.current_token.value
            self.advance()
            if self.current_token and self.current_token.type == TokenType.EQUAL:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.LBRACKET:
                    elements = self.parse_array()
                    return VarDeclNode(identifier, ArrayNode(elements))
                else:
                    self.raise_error_expect("[", self.current_token)
            else:
                self.raise_error_expect("=", self.current_token)
        else:
            self.raise_error_expect("identifier", self.current_token)

    def parse_index_access(self):
        node = self.parse_primary()
        while self.current_token and self.current_token.type == TokenType.LBRACKET:
            self.advance()
            index = self.parse_expr()
            if self.current_token and self.current_token.type == TokenType.RBRACKET:
                self.advance()
                node = IndexAccessNode(node, index)
            else:
                self.raise_error_expect("]", self.current_token)
        return node
    
    def parse_primary(self):
        token = self.current_token
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(token.value)
        elif token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL):
            self.advance()
            return LiteralNode(token)
        elif token.type == TokenType.NOTHING:
            self.advance()
            return NothingLiteralNode(None)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
                return expr
            else:
                self.raise_error_expect(")", self.current_token)
        else:
            self.raise_error(f"Unexpected token in primary: {token}")

    def parse_return_statement(self):
        self.advance()
        if self.current_token and self.current_token.type in (TokenType.SEMICOLON, TokenType.NOTHING):
            self.advance()
            return ReturnNode(NothingLiteralNode(None))
        value = self.parse_expr()
        return ReturnNode(value)
    
    # IMPORT
    def parse_import_statement(self):
        path = ""
        identifier = ""
        self.advance()
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            path += self.current_token.value
            self.advance()
            while self.current_token and self.current_token.type == TokenType.DOT:
                path += "\\"
                self.advance()
                path += self.current_token.value
                print(path)
                self.advance()

            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
                    identifier = self.current_token.value
                    self.advance()
                else:
                    self.raise_error("Expected identifier assigned to import module")
            else:
                identifier = self.peek_prev_token().value
                
            return ImportNode(name=identifier, path=path)
        else:
            self.raise_error("Expected import path")
            

    # FUNCTIONS AND METHODS
    def parse_method_call(self):
        node = VariableNode(self.current_token.value)
        self.advance()
        while self.current_token and self.current_token.type == TokenType.DOT:
            self.advance()
            method_name = self.current_token.value
            self.advance()
            self.advance()
            args = self.parse_arguments()
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")", self.current_token)
            node = MethodCallNode(node, method_name, args)
            if args and args == "error":
                self.raise_error(f"Unexpected argument error for method '{method_name}()'")
        return node

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
                if self.current_token and self.current_token.type in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.INT, TokenType.FLOAT, TokenType.BOOL, TokenType.LBRACKET, TokenType.LPAREN, TokenType.NOTHING, TokenType.NOT):
                    args.append(self.parse_expr())
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        if self.current_token and self.current_token.type == TokenType.COMMA:
                            self.advance()
                            if self.current_token and self.current_token.type not in (TokenType.IDENTIFIER, TokenType.STRING, TokenType.INT, TokenType.FLOAT, TokenType.BOOL, TokenType.LBRACKET, TokenType.LPAREN, TokenType.NOTHING):
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
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            condition = self.parse_logical_or() ### <- FIX HERE

            if self.current_token.type == TokenType.RPAREN:
                self.advance()
            else:
                self.raise_error_expect(")", self.current_token)

            # BODY
            if self.current_token.type == TokenType.COLON:
                self.advance()
                body = []
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
                    self.advance()
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
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
                if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                    self.advance()
                    condition = self.parse_logical_or()
                    if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                        self.advance()
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
            if body == []:
                self.raise_error("Body cannot be empty")
            if self.current_token and self.current_token.type == TokenType.END:
                self.advance()
            else:
                self.raise_error_expect("end")
        else:
            self.raise_error_expect(":")

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
            self.raise_error("Unexpected operator")
        return left

    def parse_expr(self):
        if self.current_token and self.current_token.type == TokenType.NOT:
            self.advance()
            return NotNode(self.parse_expr())
        else:
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
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
                return expr
            else:
                self.raise_error_expect(")", self.current_token)
        elif token.type == TokenType.LBRACKET:
            array = self.parse_array()
            return ArrayNode(array)
        elif token.type == TokenType.IDENTIFIER:
            if self.peek() and self.peek().type == TokenType.LPAREN:
                return self.parse_function_call()
            elif self.peek() and self.peek().type == TokenType.LBRACKET:
                return self.parse_index_access()
            else:
                return self.parse_index_access()  # handles simple var or chained array access
        elif token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.BOOL):
            self.advance()
            return LiteralNode(token)
        elif token.type == TokenType.NOTHING:
            self.advance()
            return NothingLiteralNode(None)
        else:
            self.raise_error(f"Unexpected token in factor: {token}")