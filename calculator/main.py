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
           '+/-', '0', ',',  '=']

def remove_digit(number_string):
    if len(number_string) == 1:
        return Decimal(0)
    else:
        return Decimal(number_string[:-1])

def add_digit(number, new_digit, add_point):
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

        for i in range(len(BUTTONS)):
            button = QPushButton(f"{BUTTONS[i]}")
            button.setFixedSize(70, 50)
            button.clicked.connect(self.make_operation)
            layout.addWidget(button, (i // 4) + 1, i % 4)

        central_widget.setLayout(layout)

    def clean_variables(self):
        self.firstNumber = None
        self.secondNumber = None
        self.result = None
        self.operation = None
        self.prev_operation = None
        self.add_point = None
        self.first_turn = True
        self.last_pressed_button = None

    def save_number(self, text):
        if self.first_turn:
            if self.firstNumber is None:
                self.firstNumber = int(text)
            elif self.result is not None:
                self.firstNumber = int(text)
                self.result = None
            else:
                self.firstNumber = add_digit(
                    self.firstNumber, text, self.add_point)

            self.label.setText(str(self.firstNumber))
        else:
            if self.secondNumber is None:
                self.secondNumber = int(text)
            else:
                self.secondNumber = add_digit(
                    self.secondNumber, text, self.add_point)
            self.label.setText(str(self.secondNumber))
            self.prev_operation = self.operation

        self.add_point = None

    def find_result(self, show_result):
        if self.secondNumber is None:
            self.secondNumber = self.firstNumber

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
        # changing for more clicking =
        self.firstNumber = self.result

        self.first_turn = True

    def save_operation(self, text):
        if self.last_pressed_button != text:
            self.label.setText(text)
            self.operation = text
            self.first_turn = False
            if self.prev_operation is None:
                self.secondNumber = None
            else:
                self.find_result(False)
                self.secondNumber = None
                self.first_turn = False

    def backspace(self):
        if self.firstNumber is not None and self.first_turn:
            self.firstNumber = remove_digit(str(self.firstNumber))
            self.label.setText(str(self.firstNumber))
        elif self.secondNumber is not None and not self.first_turn:
            self.secondNumber = remove_digit(str(self.secondNumber))
            self.label.setText(str(self.secondNumber))

    def keyPressEvent(self, event: QKeyEvent):
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
                     Qt.Key.Key_Slash, Qt.Key.Key_Percent):
            self.save_operation(chr(key))

    def make_number_with_point(self):
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
        button = self.sender()
        text = button.text()

        try:
            match text:
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
                case _ if text.isnumeric():
                    self.save_number(text)
                case _:
                    self.save_operation(text)

            self.last_pressed_button = text

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
