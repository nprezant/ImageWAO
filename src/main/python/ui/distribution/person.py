from typing import List

from PySide2 import QtWidgets

from .transect import Transect
from .draglabelcontainer import TransectContainer


class Person(QtWidgets.QWidget):
    def __init__(self, name: str):
        super().__init__()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)

        self.assignedTransectList = TransectContainer()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        self.setLayout(layout)

    def addTransect(self, transect: Transect):
        self.assignedTransectList.addDragLabel(
            f"{transect.name} ({transect.numPhotos})"
        )

    def transects(self) -> List[Transect]:
        return self.findChildren(Transect)

