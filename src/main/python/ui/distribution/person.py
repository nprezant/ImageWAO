from typing import List

from PySide2 import QtWidgets, QtCore

from base import ctx

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

        self.deleteButton: QtWidgets.QPushButton = QtWidgets.QPushButton(self)
        self.deleteButton.setIcon(ctx.closeDockIcon)
        self.deleteButton.clicked.connect(self.close)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)
        self.nameLine.setFixedWidth(self.nameLine.width())
        self.setStyleSheet(
            ":enabled { font-weight: bold; } :disabled { color: black; }"
        )
        sp: QtWidgets.QSizePolicy = self.nameLine.sizePolicy()
        sp.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.nameLine.setSizePolicy(sp)

        self.assignedTransectList = transects
        self.assignedTransectList.contentsChanged.connect(self.updateNumPhotos)

        self.numPhotosLabel = TotalCountLabel(self)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.deleteButton)
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

    def setEditable(self, editable: bool):
        if editable:
            self.nameLine.setReadOnly(False)
            self.nameLine.setDisabled(False)
            self.deleteButton.show()
        else:
            self.nameLine.setReadOnly(True)
            self.nameLine.setDisabled(True)
            self.deleteButton.hide()
