INTEGER, PLUS, MINUS, MUL, DIV, EOF, RPAREN, LPAREN, LESS, GREATER, EQUAL, NOT_EQUAL, LESS_EQ, GREATER_EQ, VARIABLE, ASSIGNMENT, RIM  = (
    'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF', 'RPAREN', 'LPAREN', 'LESS', 'GREATER', 'EQUAL', 'NOT_EQUAL', 'LESS_EQ', 'GREATER_EQ',
    'VARIABLE', 'ASSIGNMENT', 'RIM'
)
PREFIX, INFIX, POSTFIX = ('PREFIX', 'INFIX', 'POSTFIX')
NORMAL, REVERSE = ('NORMAL', 'REVERSE')
vars = {}

class Token():
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return "<{} {}>".format(self.type, self.value)

class Lexer():
    def __init__(self, text, type):
        self.text = text
        self.type = type
        if type == NORMAL:
            self.pos = 0
        else:
            self.pos = len(self.text) - 1
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Neocekivani karakter {} '.format(self.current_char))

    def advance(self):
        if self.type == NORMAL:
            self.pos += 1

            if self.pos > len(self.text) -1 :
                self.current_char = None
            else:
                self.current_char = self.text[self.pos]
        else:
            self.pos -= 1

            if self.pos < 0:
                self.current_char = None
            else:
                self.current_char = self.text[self.pos]

    def integer(self):
        number = ""
        while(self.current_char is not None and self.current_char.isdigit()):
            number += self.current_char
            self.advance()
        if self.type == NORMAL:
            return int(number)
        else:
            return int(number[::-1])

    def skip_whitespace(self):
        while(self.current_char is not None and self.current_char.isspace()):
            self.advance()

    def variable(self):
        variable = ""
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '-' or self.current_char == '_'):
            variable += self.current_char
            self.advance()
        if self.type == NORMAL:
            return variable
        else:
            return variable[::-1]

    def roman(self):
        roman = ""
        self.advance()
        while self.current_char is not None and self.current_char.isalpha():
            roman += self.current_char
            self.advance()
        self.advance()
        if self.type == NORMAL:
            return roman
        else:
            return roman[::-1]

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
                if self.type == REVERSE:
                    roman = self.roman()
                    self.advance()
                    self.advance()
                    self.advance()
                    self.advance()
                    return Token(RIM, roman)
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
                    if self.current_char == '(':
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

    def postfix_to_infix(self):
        stack = []
        token = self.current_token
        while token.type != EOF:
            if token.type == VARIABLE:
                stack.append(token.value)
            elif token.type == INTEGER:
                stack.append(str(token.value))
            elif token.type == RIM:
                stack.append('RIM(' + token.value + ')')
            else:
                op1 = stack.pop()
                op2 = stack.pop()
                if token.type in (MUL, DIV, PLUS, MINUS, ASSIGNMENT):
                    stack.append("( " + op2 + " " + token.value + " " + op1 + " )")
                else:
                    stack.append(op2 + " " + token.value + " " + op1)
            self.eat(token.type)
            token = self.current_token
        return stack.pop()

    def prefix_to_infix(self):
        stack = []
        token = self.current_token
        while token.type != EOF:
            if token.type == VARIABLE:
                stack.append(token.value)
            elif token.type == INTEGER:
                stack.append(str(token.value))
            elif token.type == RIM:
                stack.append('RIM(' + token.value + ')')
            else:
                op1 = stack.pop()
                op2 = stack.pop()
                if token.type in (MUL, DIV, PLUS, MINUS, ASSIGNMENT):
                    stack.append("( " + op1 + " " + token.value + " " + op2 + " )")
                else:
                    stack.append(op1 + " " + token.value + " " + op2)
            self.eat(token.type)
            token = self.current_token
        return stack.pop()

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

        if state == INFIX:
            lexer = Lexer(text, NORMAL)
            interpreter = Interpreter(lexer)
            result = interpreter.bool()
            print(result)
        elif state == POSTFIX:
            lexer = Lexer(text, NORMAL)
            interpreter = Interpreter(lexer)
            result = interpreter.postfix_to_infix()
            lexer = Lexer(result, NORMAL)
            interpreter = Interpreter(lexer)
            result = interpreter.bool()
            print(result)
        else:
            lexer = Lexer(text, REVERSE)
            interpreter = Interpreter(lexer)
            result = interpreter.prefix_to_infix()
            lexer = Lexer(result, NORMAL)
            interpreter = Interpreter(lexer)
            result = interpreter.bool()
            print(result)

if __name__ == "__main__":
    main()
