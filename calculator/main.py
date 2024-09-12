from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QWidget, QGridLayout
from PyQt6.QtGui import QKeyEvent, QFont
from decimal import Decimal
import sys

MAX_NUMBER = 9999999999999999
MIN_NUMBER = 0.0000000000000001
BUTTONS = ['CE', 'C', '<-', '/',
           '7', '8', '9', 'x',
           '4', '5', '6', '-',
           '1', '2', '3', '+',
           '+/-', '0', ',', '=']


def remove_digit(number_string):
    """
    This function remove last digit from number
    :param number_string: number in (string)
    :return: number without last digit (Decimal)
    """
    if len(number_string) == 1:
        return Decimal(0)
    else:
        return Decimal(number_string[:-1])


def add_digit(number, new_digit, add_point):
    """
    Function for adding any digit to number (or point for Decimal)
    :param number: number from screen
    :param new_digit: new digit
    :param add_point: flag for adding point (bool)
    :return:
    """
    if len(str(number)) < 16:
        if isinstance(number, int):
            if add_point:
                number = Decimal(str(number) + "." + new_digit)
            else:
                number = int(str(number) + new_digit)
        else:
            number = Decimal(str(number) + new_digit)
    return number


class Calculator(QMainWindow):
    """
    Class which draw window and make
    simple maths operations
    """

    def __init__(self):
        self.firstNumber = None
        self.secondNumber = None
        self.result = None
        self.operation = None
        self.prev_operation = None
        self.add_point = None
        self.last_pressed_button = None
        self.first_turn = True
        self.label = QLabel("")

        super().__init__()

        self.draw_calculator()

    def draw_calculator(self):
        """
        Function for rendering the calculator window
        """
        self.setWindowTitle("Calculator")
        self.setFixedSize(QSize(300, 500))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QGridLayout()

        self.label.setFixedSize(280, 40)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label, 0, 0, 1, 4)
        self.label.setText("0")

        font = QFont()
        font.setPointSize(17)
        font.setBold(True)

        self.label.setFont(font)

        #Adding all buttons on window
        for i in range(len(BUTTONS)):
            button = QPushButton(f"{BUTTONS[i]}")
            button.setFixedSize(70, 50)
            button.clicked.connect(self.make_operation)
            layout.addWidget(button, (i // 4) + 1, i % 4)

        central_widget.setLayout(layout)
        pass

    def clean_variables(self):
        """
        Method for cleaning all сlass fields
        """
        self.firstNumber = None
        self.secondNumber = None
        self.result = None
        self.operation = None
        self.prev_operation = None
        self.add_point = None
        self.first_turn = True
        self.last_pressed_button = None

    def save_number(self, symbol):
        """
        Function for saving digits in numbers
        :param symbol: digit or . (string)
        """
        if self.first_turn:
            if self.firstNumber is None:
                self.firstNumber = int(symbol)
            elif self.result is not None:
                self.firstNumber = int(symbol)
                self.result = None
            else:
                self.firstNumber = add_digit(
                    self.firstNumber, symbol, self.add_point)

            self.label.setText(str(self.firstNumber))
        else:
            if self.secondNumber is None:
                self.secondNumber = int(symbol)
            else:
                self.secondNumber = add_digit(
                    self.secondNumber, symbol, self.add_point)
            self.label.setText(str(self.secondNumber))
            self.prev_operation = self.operation

        self.add_point = None

    def find_result(self, show_result):
        """
        Function for calculating
        :param show_result: field which responsible
        for showing result on screen (bool)
        """
        #If the second element is not provided,
        # we will copy the first one into it.
        if self.secondNumber is None:
            self.secondNumber = self.firstNumber

        #we need prev_operation if user dont click =
        #but calculates with other operators
        if self.prev_operation is not None:
            operation = self.prev_operation
        else:
            operation = self.operation

        if isinstance(self.firstNumber, Decimal) or isinstance(self.secondNumber, Decimal):
            first_element = Decimal(self.firstNumber)
            second_element = Decimal(self.secondNumber)
        else:
            first_element = self.firstNumber
            second_element = self.secondNumber

        if operation == '+':
            self.result = first_element + second_element
        elif operation == '-':
            self.result = first_element - second_element
        elif operation == 'x' or operation == '*':
            self.result = first_element * second_element
        elif operation == '/':
            self.result = first_element / second_element
        else:
            if first_element is None:
                self.result = 0
            else:
                self.result = first_element

        if self.prev_operation is not None or show_result:
            if abs(self.result) > MAX_NUMBER or 0 < self.result < MIN_NUMBER:
                self.label.setText("{:.8e}".format(self.result))
            else:
                self.label.setText(str(self.result))

        # changing value for next operations
        self.firstNumber = self.result
        self.first_turn = True

    def save_operation(self, symbol):
        """
        Function for saving +,-,*,/,
        :param symbol: chosen operation (string)
        """
        if self.last_pressed_button != symbol:
            self.label.setText(symbol)
            self.operation = symbol
            self.first_turn = False
            if self.prev_operation is None:
                self.secondNumber = None
            else:
                self.find_result(False)
                self.secondNumber = None
                self.first_turn = False

    def backspace(self):
        """
        Method for removing last symbol from number
        """
        if self.firstNumber is not None and self.first_turn:
            self.firstNumber = remove_digit(str(self.firstNumber))
            self.label.setText(str(self.firstNumber))
        elif self.secondNumber is not None and not self.first_turn:
            self.secondNumber = remove_digit(str(self.secondNumber))
            self.label.setText(str(self.secondNumber))

    def keyPressEvent(self, event: QKeyEvent):
        """
        Method for tracking keyboard using the calculator
        :param event:
        """
        key = event.key()
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            self.save_number(chr(key))
        elif Qt.Key.Key_Equal == key:
            self.prev_operation = None
            self.find_result(True)
        elif Qt.Key.Key_Backspace == key:
            self.backspace()
        elif key in (Qt.Key.Key_Period, Qt.Key.Key_Comma):
            self.make_number_with_point()
        elif key in (Qt.Key.Key_Plus, Qt.Key.Key_Minus, Qt.Key.Key_Asterisk,
                     Qt.Key.Key_Slash):
            self.save_operation(chr(key))

        if (key in (Qt.Key.Key_Equal, Qt.Key.Key_Period,
                   Qt.Key.Key_Comma,Qt.Key.Key_Plus,
                   Qt.Key.Key_Minus, Qt.Key.Key_Asterisk,
                    Qt.Key.Key_Slash)
                or Qt.Key.Key_0 <= key <= Qt.Key.Key_9):
            self.last_pressed_button = chr(key)

    def make_number_with_point(self):
        """
        Method for adding . to numbers (Decimal)
        """
        if self.first_turn:
            if self.firstNumber is None:
                self.firstNumber = 0

            if str(self.firstNumber).find(".") == -1:
                self.label.setText(str(self.firstNumber) + ".")
        else:
            if self.secondNumber is None:
                self.secondNumber = 0

            if str(self.secondNumber).find(".") == -1:
                self.label.setText(str(self.secondNumber) + ".")

        self.add_point = True

    def make_operation(self):
        """
        Method for tracking pressed buttons
        """
        button = self.sender()
        symbol = button.text()

        try:
            match symbol:
                case 'CE':
                    if self.first_turn:
                        self.firstNumber = 0
                        self.label.setText(str(self.firstNumber))
                    else:
                        self.secondNumber = 0
                        self.label.setText(str(self.secondNumber))
                case 'C':
                    self.clean_variables()
                    self.label.setText("0")
                case '=':
                    self.prev_operation = None
                    self.find_result(True)
                case '+/-':
                    if self.first_turn:
                        if self.firstNumber is None:
                            self.firstNumber = 0
                        else:
                            self.firstNumber = -self.firstNumber
                        self.label.setText(str(self.firstNumber))
                    else:
                        self.secondNumber = -self.secondNumber
                        self.label.setText(str(self.secondNumber))
                case '<-':
                    self.backspace()
                case ',':
                    self.make_number_with_point()
                case _ if symbol.isnumeric():
                    self.save_number(symbol)
                case _:
                    self.save_operation(symbol)

            self.last_pressed_button = symbol

        except ZeroDivisionError:
            self.label.setText("you try divide by 0")
            self.clean_variables()

        except Exception as err:
            self.label.setText(err)
            self.clean_variables()


app = QApplication(sys.argv)
window = Calculator()
window.show()
app.exec()
