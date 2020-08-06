"""
This file contains widgets that can be easily overlaid on top
of other widgets, such as loading widgets that block user input.
"""

from PySide2 import QtWidgets, QtCore, QtGui

from base import ctx
from tools import clearLayout

from .overlaywidget import OverlayWidget


class LoadingOverlay(OverlayWidget):
    def __init__(self, parent):
        """
        A loading overlay screen that blocks user input and displays load progress
        over it's parent widget.
        """
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)

        # Opacity effect / animation
        self.opacityEffect = QtWidgets.QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacityEffect)
        self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b"opacity")
        self.opacityAni.setStartValue(0.0)
        self.opacityAni.setEndValue(1.0)
        self.opacityAni.setDuration(350)
        self.opacityAni.finished.connect(self._hideIfFadedOut)

        # Loading label
        self.label = QtWidgets.QLabel(
            "Loading..."
        )  # TODO: Come up with better system of setting loading text. Or add a progress bar
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.setStyleSheet(
            """
            color: rgb(80, 90, 90);
            font-size: 48px;
            font-family: arial, helvetica;
            """
        )

        # Animal images
        self.animalLabel = QtWidgets.QLabel()
        self.animalLabel.setPixmap(ctx.loadingAnimalsPixmap)
        self.animalLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.animalLabel)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Extra overlays may be involved if there are floating dock widgets
        self.extraOverlays = []

    @QtCore.Slot()
    def _hideIfFadedOut(self):
        """
        Hides this widget if it has just been fading out.
        Connected to the `finished` signal of the opacity animation.
        """
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.hide()

    @QtCore.Slot()
    def fadeOut(self):
        """
        Fades out this overlay and hides itself when fade out is complete.
        """
        # Propogate to each extra overlay attached
        for extra in self.extraOverlays:
            extra.fadeOut()

        self.opacityAni.setDirection(self.opacityAni.Backward)
        self.opacityAni.start()

    @QtCore.Slot()
    def activate(self):
        """
        Fades in the overlay and begins blocking user input.
        """

        if self.isHidden():

            # If this is a main window, we should also overlay dock widgets
            if isinstance(self.parent(), QtWidgets.QMainWindow):

                docks: QtWidgets.QDockWidget = self.parent().findChildren(
                    QtWidgets.QDockWidget
                )
                for dock in docks:
                    if dock.isFloating():
                        extra = LoadingOverlay(dock.widget())
                        clearLayout(extra.layout())  # All we want is the color
                        extra.activate()
                        self.extraOverlays.append(extra)

            # Start fading in if hidden
            self.opacityEffect.setOpacity(0)
            self.opacityAni.setDirection(self.opacityAni.Forward)
            self.opacityAni.start()
            self.show()

            # Block input
            self.grabKeyboard()
            # self.grabMouse()

    @QtCore.Slot(int)
    def setProgress(self, value):
        """
        Activates this overlay if not already active and sets the progress bar value.
        """
        self.label.setText(f"Loading... {value}%")
        self.activate()

    def hide(self):
        """
        Hides the overlay and releases the user input block.
        """
        self.releaseKeyboard()
        # self.releaseMouse()

        # Propogate to each extra overlay attached
        for extra in self.extraOverlays:
            extra.hide()

        super().hide()

    def paintEvent(self, event: QtGui.QPaintEvent):
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(100, 100, 100, 128))
        # p.setPen(QtGui.QPen(QtGui.QColor(200, 200, 255)))
        # p.setFont(QtGui.QFont('arial,helvetica', 48))
        # p.drawText(self.rect(), 'Loading...', QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        p.end()
        return super().paintEvent(event)
