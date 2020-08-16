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
        self.setLineWidth(2)
        self.setLineWidth(2)
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
            dragTransect = self.addTransect(transect)
            dragTransect.setBackgroundColor(QtGui.QColor(transectData["color"]))
            self._sortTransects()

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
        self._addDragTransect(dragTransect)
        return dragTransect

    def _addDragTransect(self, dragTransect: DragTransect):
        self.layout().insertWidget(self.layout().count() - 1, dragTransect)

    def removeTransects(self) -> List[DragTransect]:
        dragTransects = self.findChildren(DragTransect)
        [t.setParent(None) for t in dragTransects]
        return dragTransects

    def _sortTransects(self):
        dragTransects = self.removeTransects()
        dragTransects.sort(key=lambda t: t.numPhotos(), reverse=True)
        [self._addDragTransect(dt) for dt in dragTransects]

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

    @staticmethod
    def fromList(rawList: list):
        container = DragTransectContainer()
        [container.addTransect(Transect.fromDict(d)) for d in rawList]
        return container
