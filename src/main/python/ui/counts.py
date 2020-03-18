'''
Form used to add counts of animals.
'''

from PySide2 import QtCore, QtGui, QtWidgets

from .popup import PopupFrame

class CountForm(PopupFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # Form labels and controls
        animalLabel = QtWidgets.QLabel('Species', self)
        animalLabel.setAlignment(QtCore.Qt.AlignCenter)
        animalText = QtWidgets.QLineEdit(self)
        
        countLabel = QtWidgets.QLabel('Number', self)
        countLabel.setAlignment(QtCore.Qt.AlignCenter)
        countText = QtWidgets.QLineEdit(self)

        duplicateLabel = QtWidgets.QLabel('Already Counted', self)
        duplicateBox = QtWidgets.QCheckBox(self)

        notesLabel = QtWidgets.QLabel('Notes', self)
        notesText = QtWidgets.QPlainTextEdit(self)
        notesText.viewport().setAutoFillBackground(False)

        # Initialize form
        layout = QtWidgets.QGridLayout(self)

        # Prevents copy/paste/etc form from showing up
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        # Layout form items
        layout.addWidget(animalLabel, 0, 0)
        layout.addWidget(animalText, 0, 1)
        layout.addWidget(countLabel, 1, 0)
        layout.addWidget(countText, 1, 1)
        layout.addWidget(duplicateLabel, 2, 1)
        layout.addWidget(duplicateBox, 2, 0, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(notesLabel, 3, 0, 1, 2)
        layout.addWidget(notesText, 4, 0, 1, 2)

        self.setLayout(layout)
        self.adjustSize()
