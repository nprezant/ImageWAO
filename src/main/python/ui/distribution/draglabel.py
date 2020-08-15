from PySide2 import QtWidgets, QtGui, QtCore


class DragLabel(QtWidgets.QLabel):
    """The actual thing that gets dragged"""

    def __init__(self, parent, text):
        super().__init__(parent)
        self.setText(text)
        self.setAutoFillBackground(True)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._dragStartPosition = None

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
        mimeData.setText(self.text())

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
