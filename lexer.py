from dataclasses import dataclass
from enum import Enum

WHITESPACE = ' \n\t'
DIGITS = '0123456789.'
KEYWORDS = ["var", "if", "else", "while", "for", "end", "return"]
LETTERS_LOWER = 'abcdefghijklmnopqrstuvwxyz'
IDENTIFIERS_CHARS = '01234567890abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ'
RESERVED_SYMBOLS = '"''=\\;,.<>=^():+-*/'

class TokenType(Enum):
    INT = 0
    FLOAT = 1
    STRING = 2
    BOOL = 4

    PLUS = 5
    MINUS = 6
    MUL = 7
    DIV = 8
    LPAREN = 9
    RPAREN = 10
    SEMICOLON = 11

    DOT = 12
    VAR = 13
    IDENTIFIER = 14
    EQUAL = 15

    IF = 16
    ELSE = 17
    WHILE = 18
    FOR = 19
    TRUE = 20
    FALSE = 21

    LBRACE = 22
    RBRACE = 23
    COMMA = 24
    COLON = 25

    EQEQ = 26 # ==
    NOT = 27 # !
    GT = 28 # >
    LT = 29 # <
    GTEQ = 30 # >=
    LTEQ = 31 # <=
    NOTEQ = 32
    
    AND = 33
    OR = 34 #
    END = 35
    RETURN = 36

    PLUSPLUS = 37
    MINUSMINUS = 38

@dataclass
class Token:
    type: TokenType
    value: any = None

    def __repr__(self):
        return f"{self.type.name}: {self.value}"
    
class Lexer:
    def __init__(self, text):
        self.text = iter(text)
        self.advance()

    def raise_error(self, message):
        raise Exception(f"{message}")

    def skip_whitespace(self):
        while self.current_char in WHITESPACE:
            self.advance()

    def skip_comments(self):
        self.advance()
        while self.current_char not in ('/', '\n', None):
            self.advance()

        if self.current_char in ('\n', None):
            self.advance()
            return
        elif self.current_char == '/':
            self.advance()
            if self.current_char == '/':
                self.advance()
                return
            else:
                self.skip_comments()
        else:
            self.skip_comments()
            # self.raise_error("Comments left open")

    def advance(self):
        try:
            self.current_char = next(self.text)
            
        except Exception:
            self.current_char = None

    def generate_tokens(self):
        while self.current_char != None:
            if self.current_char in WHITESPACE:
                self.skip_whitespace()
            
            #BINOPS
            elif self.current_char.isdigit() or self.current_char ==  '.': # INTS/FLOATS AND DECIMALS POINTS
                yield self.generate_number()
            # elif self.current_char == '"':
            #     yield Token(TokenType.STRING, self.generate_number(self.current_char))
            elif self.current_char == '+':
                yield self.determine_plus()
            elif self.current_char == '-':
                yield self.determine_minus()
            elif self.current_char == '*':
                yield Token(TokenType.MUL, self.current_char)
                self.advance()
            elif self.current_char == '/': # HANDLES COMMENTS
                self.advance()
                print(self.current_char)
                if self.current_char == "/":
                    self.skip_comments()
                elif self.current_char == None:
                    self.raise_error(f"{self.current_char} is not recognised. Did you mean '//'")
                else:
                    yield Token(TokenType.DIV, "/")

            elif self.current_char == '(':
                yield Token(TokenType.LPAREN, self.current_char)
                self.advance()
            elif self.current_char == ')':
                yield Token(TokenType.RPAREN, self.current_char)
                self.advance()
            
            # SYMBOLS + BRACES
            elif self.current_char == ',':
                yield Token(TokenType.COMMA, self.current_char)
                self.advance()
            elif self.current_char == '{':
                yield Token(TokenType.LBRACE, self.current_char)
                self.advance()
            elif self.current_char == '}':
                yield Token(TokenType.RBRACE, self.current_char)
                self.advance()
            elif self.current_char == ';':
                yield Token(TokenType.SEMICOLON, self.current_char)
                self.advance()
            elif self.current_char == ':':
                yield Token(TokenType.COLON, self.current_char)
                self.advance()

            # EQUALS AND CONDITIONAL OP
            elif self.current_char == '=':
                yield self.determine_equals() # NO SELF.ADVANCE()
            elif self.current_char == '<':
                yield self.determine_less_than()
                self.advance()
            elif self.current_char == '>':
                yield self.determine_greater_than()
                self.advance()
            elif self.current_char == '&':
                yield self.determine_and()
                self.advance()
            elif self.current_char == '|':
                yield self.determine_or()
                self.advance()
            elif self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    yield Token(TokenType.NOTEQ, '!=')
                    self.advance()
                else:
                    yield Token(TokenType.NOT, '!')

            # STRINGS
            elif self.current_char == '"' or self.current_char == "'":
                yield self.generate_string(self.current_char)

            # IDENTIFIERS & BOOLEANS & KEYWORDS
            elif isinstance(self.current_char, str) and self.current_char in IDENTIFIERS_CHARS:
                yield self.decipher_term()

            # KEYWORDS
            elif isinstance(self.current_char, str) and self.current_char in LETTERS_LOWER:
                yield self.generate_keyword() # CHECK FOR KEYWORDS(E.G. VAR)
            else:
                self.raise_error(r"Invalid syntax")

    def determine_minus(self):
        current_symbol = self.current_char
        self.advance()
        
        if self.current_char == '-':
            current_symbol += self.current_char
            return Token(TokenType.MINUSMINUS, current_symbol)
        else:
            return Token(TokenType.MINUS, current_symbol)

    def determine_plus(self):
        current_symbol = self.current_char
        self.advance()
        
        if self.current_char == '+':
            current_symbol += self.current_char
            self.advance()
            return Token(TokenType.PLUSPLUS, current_symbol)
        else:
            return Token(TokenType.PLUS, current_symbol)

    def determine_and(self):
        current_symbol = self.current_char
        self.advance()

        if self.current_char == '&':
            current_symbol += self.current_char
            return Token(TokenType.AND, current_symbol)
        else:
            self.raise_error("Invalid Token")

    def determine_or(self):
        current_symbol = self.current_char
        self.advance()

        if self.current_char == '|':
            current_symbol += self.current_char
            return Token(TokenType.OR, current_symbol)
        else:
            self.raise_error("Invalid Token")

    def determine_less_than(self):
        current_less_than = self.current_char
        self.advance()

        if self.current_char == '=':
            current_less_than += self.current_char
            return Token(TokenType.LTEQ, current_less_than)
        else:
            return Token(TokenType.LT, current_less_than)
        
    def determine_greater_than(self):
        current_more_than = self.current_char
        self.advance()

        if self.current_char == '=':
            current_more_than += self.current_char
            return Token(TokenType.GTEQ, current_more_than)
        else:
            return Token(TokenType.GT, current_more_than)

    def determine_equals(self):
        current_eq = self.current_char
        self.advance()

        if self.current_char == '=':
            current_eq += self.current_char
            self.advance()
            return Token(TokenType.EQEQ, current_eq)
        else:
            return Token(TokenType.EQUAL, current_eq)
        
    ########################################################

    def generate_number(self):
        current_num = self.current_char
        dp_count = 0
        if self.current_char == '.':
            dp_count += 1
            
        self.advance()

        while str(self.current_char) in DIGITS and self.current_char != None:
            if str(self.current_char) in DIGITS:
                if self.current_char == '.':
                    dp_count += 1

                current_num = f"{current_num}{self.current_char}"
                self.advance()

        if dp_count <= 1:
            if dp_count > 0:
                if current_num.endswith('.') :
                    current_num = f"{current_num}{0}"
                    return Token(TokenType.FLOAT, float(current_num))
                elif current_num.startswith('.'):
                    current_num = f"{0}{current_num}"
                    return Token(TokenType.FLOAT, float(current_num))
                else:
                    return Token(TokenType.FLOAT, float(current_num))
            return Token(TokenType.INT, int(current_num))
        elif dp_count > 1:
            self.raise_error(r"Too many decimal points")

    def generate_bool(self, value):
        if value == 'True':
            return Token(TokenType.BOOL, True)
        else:
            return Token(TokenType.BOOL, False)
        
    def generate_string(self, quote_type): # INCLUDES QUOTATIONS
        if quote_type == "'" or quote_type == '"':
            current_string = self.current_char
            escape = False
            self.advance()
            
            while self.current_char is not None and (self.current_char != quote_type or escape):
                if escape:
                    if self.current_char == 'n':
                        current_string += '\n'
                    elif self.current_char == 't':
                        current_string += '\t'
                    elif self.current_char == 'b':
                        current_string += '\b'
                    elif self.current_char == '"':
                        current_string += '"'
                    elif self.current_char == "'":
                        current_string += "'"
                    elif self.current_char == '\\':
                        current_string += '\\'
                    escape = False
                else:
                    if self.current_char == '\\':
                        escape = True
                    else:
                        current_string += self.current_char

                self.advance()

            if self.current_char == quote_type:
                current_string = f"{current_string}{self.current_char}" # ADD LAST QUOTATION MARK
                self.advance()

                return Token(TokenType.STRING, str(current_string))
            else:
                self.raise_error(f"Expected ({quote_type}), got ({self.current_char})")
        else:
            self.raise_error("Missing quotations in string")
        
    def generate_keyword(self, keyword=TokenType, value=any):
        return Token(keyword, value)

    def generate_identifier(self, identifier):
        return Token(TokenType.IDENTIFIER, identifier)

    def decipher_term(self):
        if isinstance(self.current_char, str) and self.current_char != None and self.current_char not in RESERVED_SYMBOLS and self.current_char not in WHITESPACE:
            current_word = self.current_char
            self.advance()

        while isinstance(self.current_char, str) and self.current_char != None and self.current_char not in RESERVED_SYMBOLS and self.current_char not in WHITESPACE:
            current_word += self.current_char
            self.advance()
        
        # KEYWORDS > BOOLEAN > IDENTIFIER
        if current_word in KEYWORDS:
            if current_word == 'var':
                return self.generate_keyword(TokenType.VAR, current_word)
            elif current_word == 'if':
                return self.generate_keyword(TokenType.IF, current_word)
            elif current_word == 'else':
                return self.generate_keyword(TokenType.ELSE, current_word)
            elif current_word == 'while':
                return self.generate_keyword(TokenType.WHILE, current_word)
            elif current_word == 'for':
                return self.generate_keyword(TokenType.FOR, current_word)
            elif current_word == 'return':
                return self.generate_keyword(TokenType.RETURN, current_word)
            elif current_word == 'end':
                return self.generate_keyword(TokenType.END, current_word)
        elif current_word in ("True", "False"):
            return self.generate_bool(current_word)
        else:
            return self.generate_identifier(current_word)