import json
from pathlib import Path

from PySide2 import QtWidgets, QtCore

from base import config


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
                " Please read in flight info data using 'readFlightFolder'",
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

        with open(flightMetaFile, "r") as f:
            saveData: dict = json.load(f)

        expectedKeys = ["Airframe", "FlightDate", "FlightTime", "FlightNotes"]
        for key in expectedKeys:
            if key not in saveData.keys():
                raise RuntimeError(
                    f"Expected key '{key}' in flight info file '{flightMetaFile}''"
                )

        self.airframeBox.setText(saveData["Airframe"])
        self.flightDateBox.setText(saveData["FlightDate"])
        self.flightTimeBox.setText(saveData["FlightTime"])
        self.flightNotesBox.setText(saveData["FlightNotes"])

    def save(self, flightFolder: Path):
        """
        Saves the data contained in this form
        """
        saveData = {
            "Airframe": self.airframeBox.text(),
            "FlightDate": self.flightDateBox.text(),
            "FlightTime": self.flightTimeBox.text(),
            "FlightNotes": self.flightNotesBox.toPlainText(),
        }
        saveFile: Path = config.flightMetaFile(flightFolder)
        saveFile.touch(exist_ok=True)
        with open(saveFile, "w") as f:
            json.dump(saveData, f)
