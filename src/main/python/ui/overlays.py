'''
This file contains widgets that can be easily overlaid on top
of other widgets, such as loading widgets that block user input.
'''

from PySide2 import QtWidgets, QtCore, QtGui

class OverlayWidget(QtWidgets.QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.newParent()

    def newParent(self):
        if not self.parent(): return
        self.parent().installEventFilter(self)
        self.raise_()

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        '''
        Catches resize and child events from the parent widget.
        '''
        if obj == self.parent():
            if event.type() == QtCore.QEvent.Resize:
                self.resize(self.parent().size())
            elif event.type() == QtCore.QEvent.ChildAdded:
                self.raise_()
        return super().eventFilter(obj, event)

    def event(self, event: QtCore.QEvent):
        '''
        Tracks when the parent widget changes.
        '''
        if event.type() == QtCore.QEvent.ParentAboutToChange:
            if self.parent():
                self.parent().removeEventFilter(self)
            elif event.type() == QtCore.QEvent.ParentChange:
                self.newParent()
        return super().event(event)

class LoadingOverlay(OverlayWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def paintEvent(self, event: QtGui.QPaintEvent):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(100, 100, 100, 128))
        p.setPen(QtGui.QPen(QtGui.QColor(200, 200, 255)))
        p.setFont(QtGui.QFont('arial,helvetica', 48))
        p.drawText(self.rect(), 'Loading...', QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        p.end()
        return super().paintEvent(event)

