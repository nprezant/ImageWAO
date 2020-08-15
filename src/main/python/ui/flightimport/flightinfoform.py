from pathlib import Path

from PySide2 import QtWidgets, QtCore

from base import config
from flightinfo import FlightInfo


class FlightInfoForm(QtWidgets.QWidget):

    closeRequested = QtCore.Signal()

    def __init__(self):
        super().__init__()

        # flight folder to read from
        self.flightFolder = None

        # airframe
        self.airframeLabel = QtWidgets.QLabel("Airframe")
        self.airframeBox = QtWidgets.QLineEdit()

        # flight date
        self.flightDateLabel = QtWidgets.QLabel("Flight Date")
        self.flightDateBox = QtWidgets.QLineEdit()

        # flight time
        self.flightTimeLabel = QtWidgets.QLabel("Flight Time")
        self.flightTimeBox = QtWidgets.QLineEdit()

        # additional notes
        self.flightNotesLabel = QtWidgets.QLabel("Additional Notes")
        self.flightNotesBox = QtWidgets.QTextEdit()

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.airframeLabel, self.airframeBox)
        layout.addRow(self.flightDateLabel, self.flightDateBox)
        layout.addRow(self.flightTimeLabel, self.flightTimeBox)
        layout.addRow(self.flightNotesLabel, self.flightNotesBox)
        self.setLayout(layout)

    @staticmethod
    def CreateWithApplyCancel():
        w = FlightInfoForm()
        w._addApplyCancel()
        return w

    def _addApplyCancel(self):
        """
        Add apply and cancel buttons to the layout
        """
        buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )

        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)

        self.layout().addWidget(buttonBox)

    @QtCore.Slot()
    def accept(self):
        if self.flightFolder is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Flight Info",
                "Cannot save data when no flight folder is specified."
                " Please open this form by right clicking on a flight folder"
                " and selecting 'flight info'.",
            )
        else:
            self.save(self.flightFolder)
            self.closeRequested.emit()

    @QtCore.Slot()
    def reject(self):
        if self.flightFolder is not None:
            self.readFlightFolder(self.flightFolder)
        self.closeRequested.emit()

    def readFlightFolder(self, flightFolder: Path):
        """
        Populates this form based on the data in the flight folder
        """
        self.flightFolder = flightFolder

        flightMetaFile = config.flightMetaFile(flightFolder)
        if not flightMetaFile.exists():
            self.airframeBox.setText("")
            self.flightDateBox.setText("")
            self.flightTimeBox.setText("")
            self.flightNotesBox.setText("")
            return

        flightInfo = FlightInfo.readInfoFile(flightMetaFile)

        self.airframeBox.setText(flightInfo.airframe)
        self.flightDateBox.setText(flightInfo.date)
        self.flightTimeBox.setText(flightInfo.time)
        self.flightNotesBox.setText(flightInfo.notes)

    def save(self, flightFolder: Path):
        """
        Saves the data contained in this form
        """
        flightInfo = FlightInfo(
            self.airframeBox.text(),
            self.flightDateBox.text(),
            self.flightTimeBox.text(),
            self.flightNotesBox.toPlainText(),
        )
        saveFile: Path = config.flightMetaFile(flightFolder)
        flightInfo.writeInfoFile(saveFile)
