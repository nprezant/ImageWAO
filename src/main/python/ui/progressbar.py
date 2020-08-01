from PySide2 import QtCore, QtGui, QtWidgets


class QAbsoluteProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTextVisible(False)
        self.setRange(0, 100)

        # install an event filter on the parent so we
        # can resize when the parent is resized
        self.parent().installEventFilter(self)

        # create opacity effect
        self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
        self.setGraphicsEffect(self.opacityEffect)
        self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b"opacity")
        self.opacityAni.setStartValue(0.0)
        self.opacityAni.setEndValue(1.0)
        self.opacityAni.setDuration(2000)
        self.opacityAni.finished.connect(self._checkHidden)

        self.h = 10

        # style
        self.setStyleSheet(
            """
            QProgressBar {
                border: 0px solid grey;
                border-radius: 5px;
                background-color: transparent;
            }

            QProgressBar::chunk {
                background-color: #007bff; /* light blue */
                width: 20px;
            }
        """
        )

        self.hide()

    def setValue(self, val):
        """
        Reimplement from QProgressBar.
        When the value is set to 0, the progress bar will hide itself.
        When the value is set to any other number, the progress bar will show.
        """
        if val == 0:
            if not self.isHidden():
                # Fade out
                self.opacityAni.setDirection(self.opacityAni.Backward)
                self.opacityAni.start()
                return  # return so the progress bar stays full
        else:
            if self.isHidden():
                # Fade in
                self.opacityEffect.setOpacity(0)
                self.show()
                self.opacityAni.setDirection(self.opacityAni.Forward)
                self.opacityAni.start()
        super().setValue(val)

    def _checkHidden(self):
        """ If we have been fading out, we should hide the progress bar"""
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.hide()

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
