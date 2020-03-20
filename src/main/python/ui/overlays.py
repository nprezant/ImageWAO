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
        '''
        A loading overlay screen that blocks user input and displays load progress
        over it's parent widget.
        '''
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

        # Loading label
        self.label = QtWidgets.QLabel('Loading...') # TODO: Come up with better system of setting loading text. Or add a progress bar
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.label.setStyleSheet(
            '''
            color: rgb(80, 90, 90);
            font-size: 48px;
            font-family: arial, helvetica;
            '''
        )

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    @QtCore.Slot()
    def activate(self):
        '''
        Shows the overlay and begins blocking user input.
        '''
        self.show()
        self.grabKeyboard()

    @QtCore.Slot(int)
    def setProgress(self, value):
        '''
        Activates this overlay if not already active and sets the progress bar value.
        '''
        self.label.setText(f'Loading... {value}%')
        self.activate()

    def hide(self):
        '''
        Hides the overlay and releases the user input block.
        '''
        self.releaseKeyboard()
        super().hide()

    def paintEvent(self, event: QtGui.QPaintEvent):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(100, 100, 100, 128))
        # p.setPen(QtGui.QPen(QtGui.QColor(200, 200, 255)))
        # p.setFont(QtGui.QFont('arial,helvetica', 48))
        # p.drawText(self.rect(), 'Loading...', QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        p.end()
        return super().paintEvent(event)

