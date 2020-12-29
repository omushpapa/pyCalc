import logging
import math
import operator
import tokenize
import typing
from decimal import Decimal
from io import StringIO

logger = logging.getLogger(__name__)

LEFT_PAREN = '('
RIGHT_PAREN = ')'
OPERATORS = {
    '(': {
        'precedence': 0,
    },
    '+': {
        'precedence': 1,
        'function': operator.add,
    },
    '-': {
        'precedence': 1,
        'function': operator.sub,
    },
    'neg': {
        'precedence': 2,
        'function': operator.neg,
    },
    '*': {
        'precedence': 3,
        'function': operator.mul,
    },
    '/': {
        'precedence': 4,
        'function': operator.truediv,
    },
    '%': {
        'precedence': 5,
        'function': lambda x: x / 100
    },
    '!': {
        'precedence': 5,
        'function': math.factorial,
    }
}


def to_postfix(expression):
    tokens = get_tokens(expression)

    operations = []
    postfix = []

    for i, token in enumerate(tokens):
        if not token.strip():
            continue

        if token == LEFT_PAREN:
            operations.append(token)

        elif token == RIGHT_PAREN:
            top_operation = operations.pop()
            while top_operation != LEFT_PAREN:
                postfix.append(top_operation)
                top_operation = operations.pop()

        elif token in OPERATORS:
            while operations and OPERATORS[token]['precedence'] <= OPERATORS[operations[-1]]['precedence']:
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
        token_string = token[1]
        if token_string:
            if token_string == '-':
                if not final_tokens or (final_tokens and final_tokens[-1] in OPERATORS):
                    swap_indexes.append(len(final_tokens))

            final_tokens.append(token_string)

    for index in swap_indexes:
        number = final_tokens[index + 1]
        final_tokens[index] = number
        final_tokens[index + 1] = 'neg'

    return final_tokens


def evaluate(expression):
    operations = to_postfix(expression)
    logger.debug(f'postfix: {operations}')

    results = []
    for token in operations:
        if token in OPERATORS:
            function: typing.Callable = OPERATORS[token]['function']

            if token in ('neg', '%',):
                operand = results.pop()
                result = function(Decimal(operand))

            elif token == '!':
                operand = results.pop()
                result = function(float(operand))

            else:
                second_operand = results.pop()
                first_operand = results.pop()

                result = function(Decimal(first_operand), Decimal(second_operand))

            logger.debug(f'applied {token} to get {result}')
            results.append(result)

        else:
            results.append(token)

    return results[-1]
