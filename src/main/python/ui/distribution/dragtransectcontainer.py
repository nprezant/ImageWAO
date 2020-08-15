import json
from typing import List

from PySide2 import QtWidgets, QtGui, QtCore

from .transect import Transect
from .dragtransect import DragTransect


class DragTransectContainer(QtWidgets.QFrame):
    """The widget that can accept the drag and
    drop events from Transects.
    """

    def __init__(self):
        super().__init__()

        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)
        self.setLayout(QtWidgets.QHBoxLayout())
        self.layout().addStretch()
        self.setAcceptDrops(True)
        self.setMinimumSize(400, 100)

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
        else:
            event.ignore()

    def addTransect(self, transect: Transect) -> DragTransect:
        dragTransect = DragTransect(self, transect)
        self.layout().insertWidget(self.layout().count() - 1, dragTransect)
        return dragTransect

    def removeTransects(self) -> List[DragTransect]:
        dragTransects = self.findChildren(DragTransect)
        [t.setParent(None) for t in dragTransects]
        return dragTransects
