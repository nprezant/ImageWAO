'''
Form used to add counts of animals.
'''

from PySide2 import QtCore, QtGui, QtWidgets

from base import config
from tools import setPlainTextEditHeight

from .popup import PopupFrame

class CountForm(PopupFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # Prevents copy/paste/etc form from showing up
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        # Form labels and controls
        animalLabel = QtWidgets.QLabel('Species', self)
        animalLabel.setAlignment(QtCore.Qt.AlignCenter)
        animalText = QtWidgets.QComboBox(self)
        animalText.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        animalText.setEditable(True)
        animalText.addItem('') # Seems to be required for placeholder text to work.
        for animal in config.searchableAnimals:
            animalText.addItem(animal)
        animalText.lineEdit().setPlaceholderText('Type to search...')
        
        countLabel = QtWidgets.QLabel('Number', self)
        countLabel.setAlignment(QtCore.Qt.AlignCenter)
        countText = QtWidgets.QSpinBox(self)
        countText.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        countText.setRange(0, 1000)
        countText.setValue(1)

        duplicateLabel = QtWidgets.QLabel('Already Counted?', self)
        duplicateLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        duplicateLabel.setToolTip(
            'If this animal (or these animals) have already been counted somewhere else, '
            'making this count a duplicate, check this box.')
        duplicateBox = QtWidgets.QCheckBox(self)

        notesLabel = QtWidgets.QLabel('Notes', self)
        notesText = QtWidgets.QPlainTextEdit(self)
        setPlainTextEditHeight(notesText, 3)
        notesText.viewport().setAutoFillBackground(False)

        # Initialize form
        layout = QtWidgets.QGridLayout(self)

        # Layout form items
        layout.addWidget(animalLabel, 0, 0)
        layout.addWidget(animalText, 0, 1, stretch=1)
        layout.addWidget(countLabel, 1, 0)
        layout.addWidget(countText, 1, 1, stretch=1)
        layout.addWidget(duplicateLabel, 2, 1, stretch=1)
        layout.addWidget(duplicateBox, 2, 0, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(notesLabel, 3, 0, 1, 2)
        layout.addWidget(notesText, 4, 0, 1, 2)

        self.setLayout(layout)
        self.adjustSize()
