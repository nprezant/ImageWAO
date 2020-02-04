
from PySide2 import QtCore, QtGui, QtWidgets

class Notifier(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addStretch(1)
        self.setLayout(layout)

        # self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('red'))
        self.setPalette(palette)

        self._reSize()

    def notify(self):
        n = Notification('Hello', 'Hello sweet world')
        self.layout().addWidget(n, QtCore.Qt.AlignBottom)
        self._reSize()
        self._rePosition()
        self.show()
        QtCore.QTimer.singleShot(10000, self._removeOldest)

    def _removeOldest(self):
        item = self.layout().takeAt(1)
        if not item:
            return

        w = item.widget()
        if w:
            w.deleteLater()

    def _reSize(self):
        w = Notification.maxWidth
        h = 0
        for _ in range(self.layout().count()-1):
            h += Notification.maxHeight
        self.setMaximumSize(w,h)
        self.setMinimumSize(w,h)

    def _rePosition(self):
        parent = self.parentWidget()

        leftBuffer = 5
        bottomBuffer = 5

        topEdge = parent.height() - self.height() - bottomBuffer
        leftEdge = parent.width() - self.width() - leftBuffer

        pos = QtCore.QPoint(leftEdge, topEdge)
        self.move(pos)


class Notification(QtWidgets.QWidget):

    maxWidth = 200
    maxHeight = 75

    def __init__(self, title, msg):
        super().__init__()

        titleLabel = QtWidgets.QLabel(title)
        msgLabel = QtWidgets.QLabel(msg)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(titleLabel)
        # layout.addWidget(msgLabel)
        self.setLayout(layout)

        self.setStyleSheet('background-color:#3285a8')

        self.setMaximumWidth(self.maxWidth)
        self.setMaximumHeight(self.maxHeight)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )

