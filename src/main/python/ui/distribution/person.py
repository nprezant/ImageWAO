from typing import List

from PySide2 import QtWidgets

from .transect import Transect
from .dragtransect import DragTransect
from .dragtransectcontainer import DragTransectContainer


class Person(QtWidgets.QWidget):
    def __init__(self, name: str):
        super().__init__()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)

        self.assignedTransectList = DragTransectContainer()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        self.setLayout(layout)

    def addTransect(self, transect: Transect):
        self.assignedTransectList.addTransect(transect)

    def removeTransects(self) -> List[DragTransect]:
        return self.assignedTransectList.removeTransects()
