import logging
import math
import operator
import tokenize
import typing
from decimal import Decimal
from enum import Enum
from io import StringIO

logger = logging.getLogger(__name__)

LEFT_PAREN = '('
RIGHT_PAREN = ')'


class Operator(typing.NamedTuple):
    symbol: str
    precedence: int
    function: typing.Callable = None


class Operators(Enum):
    LEFT_PARENTHESIS = Operator('(', 0)
    ADDITION = Operator('+', 1, operator.add)
    SUBTRACTION = Operator('-', 1, operator.sub)
    MULTIPLICATION = Operator('*', 3, operator.mul)
    DIVISION = Operator('/', 4, operator.truediv)
    PERCENTAGE = Operator('%', 5, lambda x: x / 100)
    FACTORIAL = Operator('!', 5, math.factorial)
    NEGATION = Operator('neg', 6, operator.neg)

    @classmethod
    def from_symbol(cls, symbol):
        for i in cls:
            if i.symbol == symbol:
                return i

        raise ValueError('Invalid symbol')

    @classmethod
    def is_valid_symbol(cls, symbol):
        exists = False
        for i in cls:
            if i.symbol == symbol:
                exists = True
                break

        return exists

    @property
    def precedence(self):
        return self.value.precedence

    @property
    def function(self):
        return self.value.function

    @property
    def symbol(self):
        return self.value.symbol


def to_postfix(expression):
    tokens = get_tokens(expression)

    operations = []
    postfix = []

    for i, token in enumerate(tokens):
        if token == Operators.LEFT_PARENTHESIS:
            operations.append(token)

        elif token == RIGHT_PAREN:
            top_operation = operations.pop()
            while top_operation != LEFT_PAREN:
                postfix.append(top_operation)
                top_operation = operations.pop()

        elif token in Operators:
            while operations and token.precedence <= operations[-1].precedence:
                top_operation = operations.pop()
                postfix.append(top_operation)

            operations.append(token)

        else:
            try:
                float(token)
            except (ValueError, TypeError):
                pass
            else:
                postfix.append(token)

    while operations:
        top_operation = operations.pop()
        postfix.append(top_operation)

    return postfix


def get_tokens(expression):
    tokens = tokenize.generate_tokens(StringIO(expression).readline)
    final_tokens = []
    swap_indexes = []
    for i, token in enumerate(tokens):
        logger.debug(f'parsing token {token}')
        token_string = token[1].strip() if token[1] else token[1]
        if token_string:
            if token_string == '-':
                if not final_tokens or (final_tokens and final_tokens[-1] in Operators):
                    swap_indexes.append(len(final_tokens))

            try:
                float(token_string)
            except ValueError:
                final_tokens.append(Operators.from_symbol(token_string))
            else:
                final_tokens.append(token_string)

    for index in swap_indexes:
        final_tokens[index] = final_tokens[index + 1]
        final_tokens[index + 1] = Operators.NEGATION

    return final_tokens


def evaluate(expression):
    operations = to_postfix(expression)
    logger.debug(f'postfix: {operations}')

    results = []
    for token in operations:
        if token in Operators:
            if token in (Operators.NEGATION, Operators.PERCENTAGE,):
                operand = results.pop()
                result = token.function(Decimal(operand))

            elif token == Operators.FACTORIAL:
                operand = results.pop()
                result = token.function(float(operand))

            else:
                second_operand = results.pop()
                first_operand = results.pop()

                result = token.function(Decimal(first_operand), Decimal(second_operand))

            logger.debug(f'applied {token} to get {result}')
            results.append(result)

        else:
            results.append(token)

    return results[-1]
