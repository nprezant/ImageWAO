from pathlib import Path

from PySide2 import QtWidgets


class FlightInfoForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

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

    def readFlightFolder(self, flightFolder: Path):
        """
        Populates this form based on the data in the flight folder
        """
        print(f"reading folder: {flightFolder}")

    def save(self, flightFolder: Path):
        """
        Saves the data contained in this form
        """
        print(f"saving to folder: {flightFolder}")
