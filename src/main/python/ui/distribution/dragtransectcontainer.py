import json
from typing import List

from PySide2 import QtWidgets, QtGui, QtCore

from .transect import Transect
from .dragtransect import DragTransect


class DragTransectContainer(QtWidgets.QFrame):
    """The widget that can accept the drag and
    drop events from Transects.
    """

    contentsChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addStretch()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasFormat("text/plain"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        pass

    def dropEvent(self, event: QtGui.QDropEvent):
        if event.mimeData().hasText():
            mime = event.mimeData()
            transectData = json.loads(mime.text())

            transect = Transect(transectData["name"], transectData["numPhotos"])
            self.addTransect(transect)

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
            else:
                event.setDropAction(QtCore.Qt.MoveAction)

            event.accept()
            self.contentsChanged.emit()
        else:
            event.ignore()

    def addTransect(self, transect: Transect) -> DragTransect:
        dragTransect = DragTransect(self, transect)
        dragTransect.removed.connect(self.contentsChanged.emit)
        self.layout().insertWidget(self.layout().count() - 1, dragTransect)
        return dragTransect

    def removeTransects(self) -> List[DragTransect]:
        dragTransects = self.findChildren(DragTransect)
        [t.setParent(None) for t in dragTransects]
        return dragTransects

    def numPhotos(self):
        """Summed number of photos from all contained DragTransects"""
        dragTransects = self.findChildren(DragTransect)
        numPhotos = 0
        for dragTransect in dragTransects:
            if not dragTransect.aboutToBeRemoved:
                numPhotos += dragTransect.numPhotos()
        return numPhotos

    def toList(self):
        return [t.toDict() for t in self.findChildren(DragTransect)]
