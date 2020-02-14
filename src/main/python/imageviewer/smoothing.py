
from PySide2 import QtCore, QtGui, QtWidgets

class QSmoothGraphicsView(QtWidgets.QGraphicsView):
    '''Implements smooth mouse/keyboard navigation'''

    def __init__(self):
        super().__init__()
        
        self._numScheduledScalings = 0
        self._numScheduledHTranslations = 0
        self._numScheduledVTranslations = 0

        self.animatingH = False
        self.animatingV = False

        self.controlDown = False

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key_Up:
            self.translateVerticalEvent(-100)
        elif key == QtCore.Qt.Key_Down:
            self.translateVerticalEvent(100)
        elif key == QtCore.Qt.Key_Left:
            self.translateHorizontalEvent(-100)
        elif key == QtCore.Qt.Key_Right:
            self.translateHorizontalEvent(100)
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.zoom(75)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            super().wheelEvent(event)
        else:
            self.zoom(event.angleDelta().y() / 8)

    def zoom(self, numDegrees):
        numSteps = numDegrees / 15
        self._numScheduledScalings += numSteps

        if (self._numScheduledScalings * numSteps < 0): # if user moved the wheel in another direction, we reset previously scheduled scalings
            self._numScheduledScalings = numSteps

        anim = QtCore.QTimeLine(350, self)
        anim.setUpdateInterval(20)

        anim.valueChanged.connect(self.scalingTime)
        anim.finished.connect(self.scaleAnimFinished)
        anim.start()

    def scalingTime(self, x):
        factor = 1 + self._numScheduledScalings / 300.0
        self.scaleView(factor)

    def scaleAnimFinished(self):
        if (self._numScheduledScalings > 0):
            self._numScheduledScalings -= 1
        else:
            self._numScheduledScalings += 1
        self.sender().deleteLater()

    def translateVertical(self, dy):
        bar = self.verticalScrollBar()
        bar.setValue(bar.value() + dy)

    def translateHorizontal(self, dx):
        bar = self.horizontalScrollBar()
        bar.setValue(bar.value() + dx)

    def translateHorizontalEvent(self, dx):
        numSteps = dx * 20
        self._numScheduledHTranslations += numSteps

        if (self._numScheduledHTranslations * numSteps < 0): # if user moved the wheel in another direction, we reset previously scheduled scalings
            self._numScheduledHTranslations = numSteps

        if not self.animatingH:
            anim = QtCore.QTimeLine(350, self)
            anim.setUpdateInterval(10)

            anim.valueChanged.connect(self.translateHTime)
            anim.finished.connect(self.translateHAnimFinished)
            anim.start()

    def translateHTime(self, x):
        if self._numScheduledHTranslations > 0:
            dx = 10
        else:
            dx = -10
        self.translateHorizontal(dx)

    def translateHAnimFinished(self):
        if (self._numScheduledHTranslations > 0):
            self._numScheduledHTranslations -= 1
        else:
            self._numScheduledHTranslations += 1
        self.sender().deleteLater()
        self.animatingH = False

    def translateVerticalEvent(self, dy):
        numSteps = dy * 20
        self._numScheduledVTranslations += numSteps

        if (self._numScheduledVTranslations * numSteps < 0): # if user moved the wheel in another direction, we reset previously scheduled scalings
            self._numScheduledVTranslations = numSteps

        if not self.animatingV:
            anim = QtCore.QTimeLine(350, self)
            anim.setUpdateInterval(10)

            anim.valueChanged.connect(self.translateVTime)
            anim.finished.connect(self.translateVAnimFinished)
            anim.start()

    def translateVTime(self, y):
        if self._numScheduledVTranslations > 0:
            dy = 10
        else:
            dy = -10

        # dy = self._numScheduledVTranslations / 500
        self.translateVertical(dy)

    def translateVAnimFinished(self):
        if (self._numScheduledVTranslations > 0):
            self._numScheduledVTranslations -= 1
        else:
            self._numScheduledVTranslations += 1
        self.sender().deleteLater()
        self.animatingV = False

    def scaleView(self, scaleFactor):
        # TODO: Set a maximum and minimum scale size
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if (factor < 0.02 or factor > 100):
            return

        self.scale(scaleFactor, scaleFactor)
