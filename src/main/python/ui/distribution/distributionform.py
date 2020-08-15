from pathlib import Path

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


class DragLabelContainer(QtWidgets.QWidget):
    """The widget that can accept the drag and
    drop events from DragLabels.
    """

    def __init__(self):
        super().__init__()

        newPalette = self.palette()
        newPalette.setColor(QtGui.QPalette.Window, QtCore.Qt.blue)
        self.setPalette(newPalette)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(DragLabel(self, "hello"))
        layout.addWidget(DragLabel(self, "another one"))
        self.setLayout(layout)

        self.setStyleSheet("DragLabelContainer { border: blue }")
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
            name = mime.text()

            self.layout().addWidget(DragLabel(self, name))

            if event.source() in self.children():
                event.setDropAction(QtCore.Qt.MoveAction)
            else:
                event.setDropAction(QtCore.Qt.CopyAction)

            event.accept()
        else:
            event.ignore()


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        transectListContainer1 = DragLabelContainer()
        transectListContainer2 = DragLabelContainer()

        vBoxLayout = QtWidgets.QVBoxLayout()
        vBoxLayout.addWidget(transectListContainer1)
        vBoxLayout.addWidget(transectListContainer2)

        self.setLayout(vBoxLayout)

    def readFlightFolder(self, flightFolder: Path):
        print(f"reading flight folder {flightFolder}")
