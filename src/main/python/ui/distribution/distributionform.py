from pathlib import Path

from PySide2 import QtWidgets


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

    def readFlightFolder(self, flightFolder: Path):
        print(f"reading flight folder {flightFolder}")
