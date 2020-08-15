import json

from PySide2 import QtWidgets, QtGui, QtCore

from .transect import Transect


class DragTransect(QtWidgets.QLabel):
    """The actual thing that gets dragged"""

    removed = QtCore.Signal()

    def __init__(self, parent, transect: Transect):
        super().__init__(parent)
        self.transect = transect

        text = f"{transect.name} ({transect.numPhotos})"
        self.setText(text)
        self.setToolTip(text)

        self._dragStartPosition = None
        self.aboutToBeRemoved = False
        self._setupUi()

    def _setupUi(self):
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setLineWidth(3)
        self.setMidLineWidth(3)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAlignment(QtCore.Qt.AlignCenter)

        font: QtGui.QFont = self.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        self.setFont(font)
        self.adjustSize()
        self.setStyleSheet("DragTransect{background-color: #008080; color: white;}")

        self.setMaximumWidth(self.width())
        self.setMaximumHeight(3 * self.fontMetrics().height())
        self.setMinimumWidth(self.width() / 3)
        self.setMinimumHeight(self.height() * 1.2)

    def toDict(self):
        return self.transect.toDict()

    def sizeHint(self):
        """Adjust size hint width to be slightly larger than the default"""
        size: QtCore.QSize = super().sizeHint()
        return QtCore.QSize(size.width() + 10, size.height())

    def numPhotos(self):
        return self.transect.numPhotos

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

        hotSpot = event.pos()

        mimeData = QtCore.QMimeData()
        mimeData.setText(json.dumps(self.transect.toDict()))

        pixmap = QtGui.QPixmap(self.size())
        self.render(pixmap)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotSpot)

        self.hide()

        dropAction: QtCore.Qt.DropAction = drag.exec_(
            QtCore.Qt.MoveAction | QtCore.Qt.CopyAction
        )

        if dropAction == QtCore.Qt.MoveAction:
            self.close()
            self.update()
            self.aboutToBeRemoved = True
            self.removed.emit()
            self.aboutToBeRemoved = False
        else:
            self.show()
