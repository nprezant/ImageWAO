
from PySide2 import QtCore, QtGui, QtWidgets

class QAbsoluteProgressBar(QtWidgets.QProgressBar):

    def __init__(self, parent):
        super().__init__(parent)

        self.setTextVisible(False)
        self.setRange(0, 100)

        # install an event filter on the parent so we
        # can resize when the parent is resized
        self.parent().installEventFilter(self)

        self.h = 10

        self.hide()

    def setValue(self, val):
        ''' Reimplement from QProgressBar.
        When the value is set to 0, the progress bar will hide itself.
        When the value is set to any other number, the progress bar will show.
        '''
        if val == 0:
            self.hide()
        else:
            if self.isHidden():
                self.show()
        super().setValue(val)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            parentRect = self.parent().rect()
            geo = self.geometry()

            # move top left to the top left of the parent
            geo.moveTopLeft(parentRect.topLeft())

            # stretch the full width
            geo.setWidth(parentRect.width())

            # ensure constant height
            geo.setHeight(self.h)

            self.setGeometry(geo)

        return super().eventFilter(source, event)
