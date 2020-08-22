from pathlib import Path

from PySide2 import QtWidgets, QtCore, QtGui

from base import config


class MigrationLogForm(QtWidgets.QWidget):

    closeRequested = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setWordWrapMode(QtGui.QTextOption.NoWrap)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    @QtCore.Slot()
    def accept(self):
        self.closeRequested.emit()

    def readTransectFolder(self, transectFolder: Path):
        """
        Populates this form based on the data in the flight folder
        """

        logFile = config.transectMigrationLog(transectFolder)
        if not logFile.exists():
            self.textEdit.setText("")
            return

        with open(logFile, "r") as f:
            logText = f.read()

        self.textEdit.setText(logText)
