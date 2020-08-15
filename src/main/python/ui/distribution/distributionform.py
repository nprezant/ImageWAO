from pathlib import Path

from PySide2 import QtWidgets, QtGui, QtCore

from .draglabelcontainer import DragLabelContainer


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        transectListContainer1 = DragLabelContainer()
        transectListContainer2 = DragLabelContainer()

        vBoxLayout = QtWidgets.QVBoxLayout()
        vBoxLayout.addWidget(transectListContainer1)
        vBoxLayout.addWidget(transectListContainer2)

        self.setLayout(vBoxLayout)

    def readFlightFolder(self, flightFolder: Path):
        print(f"reading flight folder {flightFolder}")
