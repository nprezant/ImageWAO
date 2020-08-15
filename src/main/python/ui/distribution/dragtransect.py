import json

from PySide2 import QtWidgets, QtGui, QtCore

from .transect import Transect


class DragTransect(QtWidgets.QLabel):
    """The actual thing that gets dragged"""

    def __init__(self, parent, transect: Transect):
        super().__init__(parent)
        self.name = transect.name
        self.numPhotos = transect.numPhotos

        text = f"{transect.name} ({transect.numPhotos})"
        self.setText(text)
        self.setToolTip(text)

        self._dragStartPosition = None
        self._setupUi()

    def _setupUi(self):
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(3)
        self.setMidLineWidth(3)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setStyleSheet("background-color: yellow; color: blue;")

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._dragStartPosition = event.pos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if not (event.buttons() and QtCore.Qt.LeftButton):
            return
        if (
            event.pos() - self._dragStartPosition
        ).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        print("I am dragging")

        hotSpot = event.pos()

        mimeData = QtCore.QMimeData()
        mimeData.setText(json.dumps({"name": self.name, "numPhotos": self.numPhotos}))

        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotSpot)

        dropAction: QtCore.Qt.DropAction = drag.exec_(
            QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
        )

        if dropAction == QtCore.Qt.MoveAction:
            print("removing myself, yw")
            self.close()
            self.update()
