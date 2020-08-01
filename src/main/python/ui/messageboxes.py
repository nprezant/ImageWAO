"""
Message boxes used in the interface
"""

from PySide2 import QtWidgets


class DoYouWantToSave(QtWidgets.QMessageBox):
    def __init__(self):
        super().__init__()
        self.setText("The transect has been modified.")
        self.setInformativeText("Do you want to save your changes?")
        self.setStandardButtons(
            QtWidgets.QMessageBox.Save
            | QtWidgets.QMessageBox.Discard
            | QtWidgets.QMessageBox.Cancel
        )
        self.setDefaultButton(QtWidgets.QMessageBox.Save)
