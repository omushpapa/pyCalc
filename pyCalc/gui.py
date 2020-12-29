#! /usr/bin/env python3

import base64
import logging
import math
import operator
import tkinter as tk
import tokenize
from decimal import Decimal
from io import StringIO
from tkinter import ttk

from screeninfo import get_monitors

from icons import icon_string

PRECEDENCE = {
    '(': 0,
    '+': 1,
    '-': 1,
    'neg': 1,
    '*': 3,
    '/': 4,
}

OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    'neg': operator.neg,
}

LEFT_PAREN = '('
RIGHT_PAREN = ')'


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
            while operations and PRECEDENCE[token] < PRECEDENCE[operations[-1]]:
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
                if not final_tokens or (final_tokens and final_tokens[-1] in PRECEDENCE):
                    swap_indexes.append(len(final_tokens))

            final_tokens.append(token_string)

    for index in swap_indexes:
        number = final_tokens[index + 1]
        final_tokens[index] = number
        final_tokens[index + 1] = 'neg'

    return final_tokens


def evaluate(expression):
    operations = to_postfix(expression)

    results = []
    for token in operations:
        if token == 'neg':
            operand = results.pop()

            result = operator.neg(Decimal(operand))
            results.append(result)

        elif token in OPERATORS:
            second_operand = results.pop()
            first_operand = results.pop()

            result = OPERATORS[token](Decimal(first_operand), Decimal(second_operand))
            results.append(result)

        else:
            results.append(token)

    return results[-1]


class TkGUI(tk.Tk):
    FONT_LARGE = ("Calibri", 12)  # selects the font of the text inside buttons
    FONT_MED = ("Calibri", 10)

    # Max rows and columns in the GUI
    MAX_ROW = 4
    MAX_COLUMN = 5
    i = 0
    NEW_OPERATION = False

    def __init__(self):
        super().__init__()

        self.title('Calculator')
        self.resizable(width=False, height=False)

        # center
        # w, h = 260, 160
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        monitors = get_monitors()
        monitor = monitors[0]
        ws, hs = monitor.width, monitor.height
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.geometry(f'+{x}+{y}')

        # Configure default theme
        style = ttk.Style(self)
        style.theme_use('clam')

        # Configure icon
        icon_data = base64.b64decode(icon_string)
        self.icon = tk.PhotoImage(data=icon_data)
        self.tk.call('wm', 'iconphoto', self._w, self.icon)

        for row in range(self.MAX_ROW):
            self.columnconfigure(row, pad=3)

        for column in range(self.MAX_COLUMN):
            self.rowconfigure(column, pad=3)

        self.display = tk.Entry(self, font=("Calibri", 13))
        self.display.grid(row=1, columnspan=6, sticky=tk.W + tk.E)

        self._init_ui()

    def _init_ui(self):
        one = tk.Button(
            self, text="1", command=lambda: self.get_variables(1), font=self.FONT_LARGE)
        one.grid(row=2, column=0)
        two = tk.Button(
            self, text="2", command=lambda: self.get_variables(2), font=self.FONT_LARGE)
        two.grid(row=2, column=1)
        three = tk.Button(
            self, text="3", command=lambda: self.get_variables(3), font=self.FONT_LARGE)
        three.grid(row=2, column=2)

        four = tk.Button(
            self, text="4", command=lambda: self.get_variables(4), font=self.FONT_LARGE)
        four.grid(row=3, column=0)
        five = tk.Button(
            self, text="5", command=lambda: self.get_variables(5), font=self.FONT_LARGE)
        five.grid(row=3, column=1)
        six = tk.Button(
            self, text="6", command=lambda: self.get_variables(6), font=self.FONT_LARGE)
        six.grid(row=3, column=2)

        seven = tk.Button(
            self, text="7", command=lambda: self.get_variables(7), font=self.FONT_LARGE)
        seven.grid(row=4, column=0)
        eight = tk.Button(
            self, text="8", command=lambda: self.get_variables(8), font=self.FONT_LARGE)
        eight.grid(row=4, column=1)
        nine = tk.Button(
            self, text="9", command=lambda: self.get_variables(9), font=self.FONT_LARGE)
        nine.grid(row=4, column=2)

        cls = tk.Button(self, text="AC", command=self.clear_all,
                        font=self.FONT_LARGE, foreground="red")
        cls.grid(row=5, column=0)
        zero = tk.Button(
            self, text="0", command=lambda: self.get_variables(0), font=self.FONT_LARGE)
        zero.grid(row=5, column=1)
        result = tk.Button(self, text="=", command=self.calculate,
                           font=self.FONT_LARGE, foreground="red")
        result.grid(row=5, column=2)

        plus = tk.Button(
            self, text="+", command=lambda: self.get_operation("+"), font=self.FONT_LARGE)
        plus.grid(row=2, column=3)
        minus = tk.Button(
            self, text="-", command=lambda: self.get_operation("-"), font=self.FONT_LARGE)
        minus.grid(row=3, column=3)
        multiply = tk.Button(
            self, text="*", command=lambda: self.get_operation("*"), font=self.FONT_LARGE)
        multiply.grid(row=4, column=3)
        divide = tk.Button(
            self, text="/", command=lambda: self.get_operation("/"), font=self.FONT_LARGE)
        divide.grid(row=5, column=3)

        # adding new operations
        pi = tk.Button(self, text="pi", command=lambda: self.get_operation(
            "*3.14"), font=self.FONT_LARGE)
        pi.grid(row=2, column=4)
        modulo = tk.Button(
            self, text="%", command=lambda: self.get_operation("%"), font=self.FONT_LARGE)
        modulo.grid(row=3, column=4)
        left_bracket = tk.Button(
            self, text="(", command=lambda: self.get_operation("("), font=self.FONT_LARGE)
        left_bracket.grid(row=4, column=4)
        exp = tk.Button(self, text="exp",
                        command=lambda: self.get_operation("**"), font=self.FONT_MED)
        exp.grid(row=5, column=4)

        # To be added :
        # sin, cos, log, ln
        undo_button = tk.Button(
            self, text="<-", command=self.undo, font=self.FONT_LARGE, foreground="red")
        undo_button.grid(row=2, column=5)
        fact = tk.Button(
            self, text="x!", command=lambda: self.factorial("!"), font=self.FONT_LARGE)
        fact.grid(row=3, column=5)
        right_bracket = tk.Button(
            self, text=")", command=lambda: self.get_operation(")"), font=self.FONT_LARGE)
        right_bracket.grid(row=4, column=5)
        square = tk.Button(
            self, text="^2", command=lambda: self.get_operation("**2"), font=self.FONT_MED)
        square.grid(row=5, column=5)

    def factorial(self, operator):
        """Calculates the factorial of the number entered."""
        try:
            number = int(self.display.get())
            result = math.factorial(number)
            self.output(str(result))
        except Exception:
            self.output("Error")

    def clear_all(self, new_operation=True):
        """clears all the content in the Entry widget."""
        self.display.delete(0, tk.END)
        self.NEW_OPERATION = new_operation

    def get_variables(self, num):
        """Gets the user input for operands and puts it inside the entry widget.

        If a new operation is being carried out, then the display is cleared.
        """
        if self.NEW_OPERATION:
            self.clear_all(new_operation=False)
        self.display.insert(self.i, num)
        self.i += 1

    def get_operation(self, operator):
        """Gets the operand the user wants to apply on the functions."""
        length = len(operator)
        self.display.insert(self.i, operator)
        self.i += length

    def undo(self):
        """removes the last entered operator/variable from entry widget."""
        whole_string = self.display.get()
        if len(whole_string):  # repeats until
            # now just decrement the string by one index
            new_string = whole_string[:-1]
            self.output(new_string, new_operation=False)
        else:
            self.output("Error, press AC")

    def calculate(self):
        """Evaluates the expression."""
        whole_string = self.display.get()
        try:
            result = evaluate(whole_string)
        except Exception:
            result = 'Error!'

        self.output(result)

    def output(self, text='', new_operation=True):
        self.clear_all(new_operation)
        self.display.insert(0, text)

    def run(self):
        """Initiate event loop."""
        self.mainloop()
