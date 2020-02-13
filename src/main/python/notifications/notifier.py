
from enum import Enum

from PySide2 import QtCore, QtGui, QtWidgets

from .toaster import QToaster

class AnimationState(Enum):
    JustAdded = 1
    AboutToRemove = 2

class Notifier:

    # constant margins
    SIDE_MARGIN = 36
    BOTTOM_MARGIN = 10
    BOTTOM_SCREEN_MARGIN = 46

    def __init__(self):
        super().__init__()
        
        self._widgets = []
        self._futureAnimations = []
        self._setAnimatingOff()

    def notify(self):
        QToaster.showMessage(
            self, 'Hello sweet world', corner=QtCore.Qt.BottomRightCorner, desktop=False
        )
        # n = Notification('Hello', 'Hello sweet world')
        # self._addWidget(n)

    def _addWidget(self, w):
        if self._animating == True:
            self._futureAnimations.append(
                (AnimationState.JustAdded, w)
            )
        else:
            self._animating = True
            self._widgets.append(w)
            self._animate(AnimationState.JustAdded, w)
            QtCore.QTimer.singleShot(5000, lambda: self._removeWidget(w))

    def _checkNextAnimation(self):

        if self._animating == True:
            return

        if len(self._futureAnimations) > 0:
            params = self._futureAnimations.pop(0)
            self._animate(*params)
            QtCore.QTimer.singleShot(5000, lambda: self._removeWidget(params[1]))

    def _setAnimatingOn(self):
        self._animating = True
    
    def _setAnimatingOff(self):
        self._animating = False

    def _getAvailableGeometry(self):
        return QtWidgets.QApplication.desktop().availableGeometry()

    def _animate(
        self,
        flag=0,
        targetWidget=None,
    ):

        # Set animation state
        self._setAnimatingOn()

        # Viewing window bounds
        availableGeometry = self._getAvailableGeometry()
        desktopWidth = availableGeometry.width()
        desktopHeight = availableGeometry.height()
        desktopX = availableGeometry.x()
        desktopY = availableGeometry.y()

        # Don't try to animate if no widgets are here
        if len(self._widgets) == 0:
            print('no widgets to animate!')
            self._setAnimatingOff()
            return

        # Keep track of the top of the widget stack
        top = desktopHeight - self.BOTTOM_SCREEN_MARGIN

        # Initialize animation group
        group = QtCore.QParallelAnimationGroup(self)
        group.finished.connect(self._setAnimatingOff)
        group.finished.connect(self._checkNextAnimation)
        loop = QtCore.QEventLoop()
        group.finished.connect(loop.quit)

        # Generate new geometries for the widgets
        for w in reversed(self._widgets):
            x = desktopWidth - w.width() - self.SIDE_MARGIN + desktopX
            y = top - w.height() - self.BOTTOM_MARGIN + desktopY
            newGeom = QtCore.QRect(x, y, w.width(), w.height())
            top = newGeom.y()
            oldGeom = w.geometry()

            if targetWidget is w:
                if flag == AnimationState.JustAdded:
                    oldGeom = QtCore.QRect(
                        newGeom.x(), newGeom.y() + 50,
                        newGeom.width(), newGeom.height(),
                    )
                    group.addAnimation(w.fadeInAnimation())
                elif flag == AnimationState.AboutToRemove:
                    newGeom = QtCore.QRect(
                        oldGeom.x(), oldGeom.y() + 50,
                        oldGeom.width(), oldGeom.height(),
                    )
                    group.addAnimation(w.fadeOutAnimation())
                    w._opacityAnimation.finished.connect(lambda: self._deleteWidget(w))
                else:
                    raise ValueError('Invalid flag')
            
            group.addAnimation(w.movementAnimation(newGeom, oldGeom))
            w.show()

        # self.show()
        group.start()
        loop.exec_()

    def _removeOldest(self):
        w = self._widgets[0]
        self._removeWidget(w)

    def _removeWidget(self, w):
        self._animate(AnimationState.AboutToRemove, w)

    def _deleteWidget(self, w):
        # self.setWindowOpacity(0)
        self._widgets.remove(w)
        w.deleteLater()

class Notification(QtWidgets.QWidget):

    def __init__(self, title, msg):
        super().__init__()

        titleLabel = QtWidgets.QLabel(title)
        msgLabel = QtWidgets.QLabel(msg)

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | # No window decoration
            QtCore.Qt.Tool | # Display in a separate window
            QtCore.Qt.WindowStaysOnTopHint # Always on top
        )

        # Tells Qt that the background will be transparent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Shows widget without focusing on it
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(titleLabel)
        layout.addWidget(msgLabel)
        self.setLayout(layout)

        self.adjustSize()

        self.setStyleSheet('background-color:#3285a8')

        # Geometry animation
        self._geometryAnimation = None

        # Opacity animation
        effect = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self._opacityAnimation = QtCore.QPropertyAnimation(
            self,
            propertyName=b'opacity',
            targetObject=effect,
            duration=500,
            startValue=0.0,
            endValue=1.0,
        )

    def sizeHint(self):
        return QtCore.QSize(300,100)

    def movementAnimation(self, newGeom, oldGeom=None):

        if oldGeom is None:
            oldGeom = self.geometry()

        self._geometryAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        self._geometryAnimation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        self._geometryAnimation.setDuration(500)
        self._geometryAnimation.setEndValue(newGeom)
        self._geometryAnimation.setStartValue(oldGeom)
        return self._geometryAnimation

    def fadeInAnimation(self):
        # self._opacityAnimation.setDirection(QtCore.QPropertyAnimation.Forward)
        self._opacityAnimation.setStartValue(0)
        self._opacityAnimation.setStartValue(1)
        return self._opacityAnimation

    def fadeOutAnimation(self):
        # self._opacityAnimation.setDirection(QtCore.QPropertyAnimation.Backward)
        self.setWindowOpacity(1)
        self._opacityAnimation.setStartValue(1)
        self._opacityAnimation.setStartValue(0)
        return self._opacityAnimation

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing) 
    
        roundedRect = QtCore.QRect()
        roundedRect.setX(self.rect().x() + 5)
        roundedRect.setY(self.rect().y() + 5)
        roundedRect.setWidth(self.rect().width() - 10)
        roundedRect.setHeight(self.rect().height() - 10)
    
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0,180)))
        painter.setPen(QtCore.Qt.NoPen) 
    
        painter.drawRoundedRect(roundedRect, 10, 10)
        painter.end()

