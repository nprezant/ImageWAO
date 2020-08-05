"""
Form used to add counts of animals.
"""

from PySide2 import QtCore, QtGui, QtWidgets

from base import config
from drawingdata import CountData

from .popupframe import PopupFrame
from .tools import setPlainTextEditHeight


class CountPopup(PopupFrame):

    countChanged = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)
        self._countData = CountData()
        self._item = None

        self.initUi()
        self.resetForm()

    def initUi(self):

        # Prevents copy/paste/etc form from showing up
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)

        # Form labels and controls
        self.speciesLabel = QtWidgets.QLabel("Species", self)
        self.speciesLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.speciesText = QtWidgets.QComboBox(self)
        self.speciesText.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.speciesText.setEditable(True)
        self.speciesText.addItem(
            ""
        )  # Seems to be required for placeholder text to work.
        for animal in config.searchableAnimals:
            self.speciesText.addItem(animal)
        self.speciesText.lineEdit().setPlaceholderText("Type to search...")

        self.numberLabel = QtWidgets.QLabel("Number", self)
        self.numberLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.numberBox = QtWidgets.QSpinBox(self)
        self.numberBox.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.numberBox.setRange(0, 1000)

        self.duplicateLabel = QtWidgets.QLabel("Already Counted?", self)
        self.duplicateLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        self.duplicateLabel.setToolTip(
            "If this animal (or these animals) have already been counted\n"
            "somewhere else, making this count a duplicate, check this box."
        )
        self.duplicateBox = QtWidgets.QCheckBox(self)

        self.notesLabel = QtWidgets.QLabel("Notes", self)
        self.notesText = QtWidgets.QPlainTextEdit(self)
        self.notesText.setTabChangesFocus(True)
        setPlainTextEditHeight(self.notesText, 3)
        self.notesText.viewport().setAutoFillBackground(False)

        # Initialize form
        layout = QtWidgets.QGridLayout(self)

        # Layout form items
        layout.addWidget(self.speciesLabel, 0, 0)
        layout.addWidget(self.speciesText, 0, 1, stretch=1)
        layout.addWidget(self.numberLabel, 1, 0)
        layout.addWidget(self.numberBox, 1, 1, stretch=1)
        layout.addWidget(self.duplicateLabel, 2, 1, stretch=1)
        layout.addWidget(self.duplicateBox, 2, 0, alignment=QtCore.Qt.AlignHCenter)
        layout.addWidget(self.notesLabel, 3, 0, 1, 2)
        layout.addWidget(self.notesText, 4, 0, 1, 2)

        self.setLayout(layout)
        self.adjustSize()

    def resetForm(self):
        """
        Resets the form to their default values.
        """
        self._item = None
        self.setCountData(CountData())

    def setCountData(self, countData):
        """
        Set the count data and update the form values to match.
        """
        self._countData = countData
        self.speciesText.setEditText(self._countData.species)
        self.numberBox.setValue(self._countData.number)
        self.duplicateBox.setChecked(self._countData.isDuplicate)
        self.notesText.setPlainText(self._countData.notes)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """
        Close the form if enter is pressed
        """
        if event.key() in (int(QtCore.Qt.Key_Enter), int(QtCore.Qt.Key_Return)):
            self.hidePopup()
        super().keyPressEvent(event)

    def popup(self, item, pos):
        """
        Re-implement to allow the count form to track which item
        the counts belong to.
        """
        self._item = item
        countData = self._item.countData()
        self.setCountData(countData)
        super().popup(pos)
        self.speciesText.setFocus(QtCore.Qt.PopupFocusReason)

    def countData(self):
        """
        Returns the count data as displayed in the form.
        """
        return CountData(
            self.speciesText.currentText(),
            self.numberBox.value(),
            self.duplicateBox.isChecked(),
            self.notesText.toPlainText(),
        )

    def hidePopup(self):
        """
        Re-implement to emit a value changed signal if necessary and reset the form.
        """
        self.checkChanged()
        self.resetForm()
        return super().hidePopup()

    def checkChanged(self):
        """
        Checks to see if this form has changed since it's launch, and if so,
        emits the `countChanged` signal after updating the relevant item.
        """
        countData = self.countData()
        if not self._countData == countData:
            self._item.setCountData(countData)
            self.countChanged.emit()
