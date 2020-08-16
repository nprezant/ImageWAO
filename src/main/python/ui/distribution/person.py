from typing import List

from PySide2 import QtWidgets, QtCore

from .transect import Transect
from .dragtransect import DragTransect
from .dragtransectcontainer import DragTransectContainer
from .totalcountlabel import TotalCountLabel


class Person(QtWidgets.QWidget):

    numPhotosUpdated = QtCore.Signal()

    def __init__(self, name: str, transects: DragTransectContainer = None):
        super().__init__()

        if transects is None:
            transects = DragTransectContainer()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)
        self.nameLine.setFixedWidth(self.nameLine.width())

        self.assignedTransectList = transects
        self.assignedTransectList.contentsChanged.connect(self.updateNumPhotos)

        self.numPhotosLabel = TotalCountLabel(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        layout.addWidget(self.numPhotosLabel)
        self.setLayout(layout)

    def addTransect(self, transect: Transect):
        self.assignedTransectList.addTransect(transect)

    def removeTransects(self) -> List[DragTransect]:
        return self.assignedTransectList.removeTransects()

    def updateNumPhotos(self):
        self.numPhotosLabel.setText(str(self.numPhotos()))
        self.numPhotosUpdated.emit()

    def numPhotos(self):
        return self.assignedTransectList.numPhotos()

    def toDict(self):
        return {
            "name": self.nameLine.text(),
            "transects": self.assignedTransectList.toList(),
        }

    @staticmethod
    def fromDict(d):
        name = d["name"]
        rawTransects = d["transects"]
        transects = DragTransectContainer.fromList(rawTransects)
        return Person(name, transects)
