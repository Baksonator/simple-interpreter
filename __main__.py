INTEGER, PLUS, MINUS, MUL, DIV, EOF, RPAREN, LPAREN, LESS, GREATER, EQUAL, NOT_EQUAL, LESS_EQ, GREATER_EQ, VARIABLE, ASSIGNMENT, RIM  = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF', 'RPAREN', 'LPAREN', 'LESS', 'GREATER', 'EQUAL', 'NOT_EQUAL', 'LESS_EQ', 'GREATER_EQ',
    'VARIABLE', 'ASSIGNMENT', 'RIM'
)
PREFIX, INFIX, POSTFIX = ('PREFIX', 'INFIX', 'POSTFIX')
vars = {}

class Token():
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return "<{} {}>".format(self.type, self.value)

class Lexer():
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Neocekivani karakter {} '.format(self.current_char))

    def advance(self):
        self.pos += 1

        if self.pos > len(self.text) -1 :
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def integer(self):
        number = ""
        while(self.current_char is not None and self.current_char.isdigit()):
            number += self.current_char
            self.advance()
        return int(number)

    def skip_whitespace(self):
        while(self.current_char is not None and self.current_char.isspace()):
            self.advance()

    def variable(self):
        variable = ""
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '-' or self.current_char == '_'):
            variable += self.current_char
            self.advance()
        return variable

    def roman(self):
        roman = ""
        if self.current_char != '(':
            self.error()
        self.advance()
        while self.current_char is not None and self.current_char.isalpha():
            roman += self.current_char
            self.advance()
        self.advance()
        return roman

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()

            if self.current_char.isdigit():
                return Token(INTEGER, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LESS_EQ, '<=')
                return Token(LESS, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GREATER_EQ, '>=')
                return Token(GREATER, '>')

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQUAL, '==')
                else:
                    return Token(ASSIGNMENT, '=')
                self.error()

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NOT_EQUAL, '!=')
                self.error()

            if self.current_char.isalpha():
                var = self.variable()
                if var == 'RIM':
                    return Token(RIM, self.roman())
                return Token(VARIABLE, var)

            self.error()

        return Token(EOF, None)

class Interpreter():
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Greska u parsiranju')

    def eat(self, type):
        if self.current_token.type == type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def roman_value(self, number):
        if number == 'I':
            return 1
        if number == 'V':
            return 5
        if number == 'X':
            return 10
        if number == 'L':
            return 50
        if number == 'C':
            return 100
        if number == 'D':
            return 500
        if number == 'M':
            return 1000
        return -1

    def roman_to_decimal(self, str):
        res = 0
        i = 0
        while (i < len(str)):
            s1 = self.roman_value(str[i])
            if (i + 1 < len(str)):
                s2 = self.roman_value(str[i + 1])
                if (s1 >= s2):
                    res = res + s1
                    i = i + 1
                else:
                    res = res + s2 - s1
                    i = i + 2
            else:
                res = res + s1
                i = i + 1
        return res

    def factor(self):
        token = self.current_token

        if token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif token.type == RIM:
            self.eat(RIM)
            return self.roman_to_decimal(token.value)
        elif token.type == VARIABLE:
            self.eat(VARIABLE)
            if self.current_token.type == EOF:
                if token.value in vars:
                    return vars[token.value]
                else:
                    vars[token.value] = None
                    return None
            elif self.current_token.type == ASSIGNMENT:
                self.eat(ASSIGNMENT)
                vars[token.value] = self.expr()
                return vars[token.value]
            elif token.value in vars and vars[token.value] is not None:
                return vars[token.value]
            else:
                return None
        elif token.type == RIM:
            pass
        elif token.type == LPAREN:
            self.eat(LPAREN)
            result = self.expr()
            self.eat(RPAREN)
            return result


    def term(self):
        result = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                result = result / self.factor()
            else:
                self.error()

        return result

    def expr(self):

        result = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                result = result + self.term()
            elif token.type == MINUS:
                self.eat(MINUS)
                result = result - self.term()
            else:
                self.error()

        return result

    def bool(self):
        result = True
        left = self.expr()

        if self.current_token.type in (LESS, GREATER, EQUAL, NOT_EQUAL, LESS_EQ, GREATER_EQ):
            right = None
            while self.current_token.type in (LESS, GREATER, EQUAL, NOT_EQUAL, LESS_EQ, GREATER_EQ):
                if self.current_token.type == LESS:
                    self.eat(LESS)
                    right = self.expr()
                    if not (left < right):
                         result = False
                    left = right
                elif self.current_token.type == GREATER:
                    self.eat(GREATER)
                    right = self.expr()
                    if not (left > right):
                         result = False
                    left = right
                elif self.current_token.type == EQUAL:
                    self.eat(EQUAL)
                    right = self.expr()
                    if not (left == right):
                         result = False
                    left = right
                elif self.current_token.type == NOT_EQUAL:
                    self.eat(NOT_EQUAL)
                    right = self.expr()
                    if not (left != right):
                         result = False
                    left = right
                elif self.current_token.type == LESS_EQ:
                    self.eat(LESS_EQ)
                    right = self.expr()
                    if not (left <= right):
                         result = False
                    left = right
                elif self.current_token.type == GREATER_EQ:
                    self.eat(GREATER_EQ)
                    right = self.expr()
                    if not (left >= right):
                         result = False
                    left = right

            return result
        else:
            return left



def main():
    state = INFIX
    while True:
        try:
            text = input(state + ' --> ')
        except EOFError:
            break

        if not text:
            continue

        if text == 'exit':
            break

        if text == 'PREFIX':
            state = PREFIX
            continue

        if text == 'INFIX':
            state = INFIX
            continue

        if text == 'POSTFIX':
            state = POSTFIX
            continue

        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.bool()
        print(result)

if __name__ == "__main__":
    main()
