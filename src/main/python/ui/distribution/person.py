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
        self._referenceNumPhotos = 0

        if transects is None:
            transects = DragTransectContainer()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)
        self.nameLine.setFixedWidth(self.nameLine.width())
        font = self.nameLine.font()
        font.setBold(True)
        self.nameLine.setFont(font)

        self.assignedTransectList = transects
        self.assignedTransectList.contentsChanged.connect(self.updateNumPhotos)

        self.numPhotosLabel = TotalCountLabel(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        layout.addWidget(self.numPhotosLabel)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def addTransect(self, transect: Transect):
        self.assignedTransectList.addTransect(transect)

    def removeTransects(self) -> List[DragTransect]:
        return self.assignedTransectList.removeTransects()

    def updateNumPhotos(self, referenceNumPhotos: int = None):
        if referenceNumPhotos is not None:
            self._referenceNumPhotos = referenceNumPhotos
        numPhotos = self.numPhotos()
        offset = numPhotos - self._referenceNumPhotos
        if offset > 0:
            sign = "+"
        else:
            sign = ""  # negative handled by number
        text = f"{numPhotos} ({sign}{offset})"
        self.numPhotosLabel.setText(text)
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
