'''
Form used to add counts of animals.
'''

from PySide2 import QtCore, QtGui, QtWidgets

from .popup import PopupFrame

class CountForm(PopupFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(100,100)
        self.setStyleSheet('''
            CountForm {
                border: 1px solid black;
                border-radius: 4px; 
                background: red;
            }
        ''')
