from PySide2 import QtCore, QtWidgets, QtGui


class QToaster(QtWidgets.QFrame):
    closed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(QToaster, self).__init__(*args, **kwargs)

        # Assign a grid layout
        QtWidgets.QGridLayout(self)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        self.setStyleSheet(
            """
            QToaster {
                border: 1px solid black;
                border-radius: 4px;
                background: palette(window);
            }
        """
        )
        # alternatively:
        # self.setAutoFillBackground(True)
        # self.setFrameShape(self.Box)

        self.timer = QtCore.QTimer(singleShot=True, timeout=self.hide)

        if self.parent():
            self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=0)
            self.setGraphicsEffect(self.opacityEffect)
            self.opacityAni = QtCore.QPropertyAnimation(self.opacityEffect, b"opacity")
            # we have a parent, install an eventFilter so that when it's resized
            # the notification will be correctly moved to the right corner
            self.parent().installEventFilter(self)
        else:
            # there's no parent, use the window opacity property, assuming that
            # the window manager supports it; if it doesn't, this won'd do
            # anything (besides making the hiding a bit longer by half a second)
            self.opacityAni = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.opacityAni.setStartValue(0.0)
        self.opacityAni.setEndValue(1.0)
        self.opacityAni.setDuration(750)
        self.opacityAni.finished.connect(self.checkClosed)

        self.geometryAni = QtCore.QPropertyAnimation(self, b"geometry")

        self.setMinimumWidth(100)
        self.setMaximumWidth(500)

        self.corner = QtCore.Qt.TopLeftCorner
        self.margin = 10
        self.isShown = False

    def checkClosed(self):
        # if we have been fading out, we're closing the notification
        if self.opacityAni.direction() == self.opacityAni.Backward:
            self.close()
            self.closed.emit()

    def restore(self):
        # this is a "helper function", that can be called from mouseEnterEvent
        # and when the parent widget is resized. We will not close the
        # notification if the mouse is in or the parent is resized
        self.timer.stop()
        # also, stop the animation if it's fading out...
        self.opacityAni.stop()
        # ...and restore the opacity
        if self.parent():
            self.opacityEffect.setOpacity(1)
        else:
            self.setWindowOpacity(1)

    def hide(self):
        # start hiding
        self.opacityAni.setDirection(self.opacityAni.Backward)
        self.opacityAni.setDuration(500)
        self.opacityAni.start()

        # geometry animation
        # geo = self.geometry()
        # geo.moveBottom(20)
        # self.geometryAni.setStartValue(self.geometry())
        # self.geometryAni.setEndValue(geo)
        # self.geometryAni.setDuration(500)

        # self.group = QtCore.QParallelAnimationGroup()
        # self.group.addAnimation(self.opacityAni)
        # self.group.addAnimation(self.geometryAni)
        # self.group.start()

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Resize:
            self.opacityAni.stop()
            parentRect = self.parent().rect()
            geo = self.geometry()
            if self.corner == QtCore.Qt.TopLeftCorner:
                geo.moveTopLeft(
                    parentRect.topLeft() + QtCore.QPoint(self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.TopRightCorner:
                geo.moveTopRight(
                    parentRect.topRight() + QtCore.QPoint(-self.margin, self.margin)
                )
            elif self.corner == QtCore.Qt.BottomRightCorner:
                geo.moveBottomRight(
                    parentRect.bottomRight() + QtCore.QPoint(-self.margin, -self.margin)
                )
            else:
                geo.moveBottomLeft(
                    parentRect.bottomLeft() + QtCore.QPoint(self.margin, -self.margin)
                )
            self.setGeometry(geo)
            self.restore()
            self.timer.start()
        return super(QToaster, self).eventFilter(source, event)

    def enterEvent(self, event):
        self.restore()

    def leaveEvent(self, event):
        self.timer.start()

    def closeEvent(self, event):
        # we don't need the notification anymore, delete it!
        self.deleteLater()

    def resizeEvent(self, event):
        super(QToaster, self).resizeEvent(event)
        # if you don't set a stylesheet, you don't need any of the following!
        if not self.parent():
            # there's no parent, so we need to update the mask
            path = QtGui.QPainterPath()
            path.addRoundedRect(QtCore.QRectF(self.rect()).translated(-0.5, -0.5), 4, 4)
            self.setMask(
                QtGui.QRegion(path.toFillPolygon(QtGui.QTransform()).toPolygon())
            )
        else:
            self.clearMask()

    def _addCloseButton(self):
        self.closeButton = QtWidgets.QToolButton()
        self.layout().addWidget(self.closeButton, 0, 2, QtCore.Qt.AlignTop)
        closeIcon = self.style().standardIcon(QtWidgets.QStyle.SP_TitleBarCloseButton)
        self.closeButton.setIcon(closeIcon)
        self.closeButton.setAutoRaise(True)
        self.closeButton.clicked.connect(self.close)
        self.closeButton.clicked.connect(self.closed.emit)

    def generate(
        self,
        message=None,
        icon=None,
        corner=QtCore.Qt.BottomRightCorner,
        margin=10,
        closable=True,
        desktop=False,
        parentWindow=True,
    ):

        parent = self.parent()
        parentRect = parent.rect()

        # For Qt standard icon pixmaps; see:
        # https://doc.qt.io/qt-5/qstyle.html#StandardPixmap-enum
        if icon is not None:
            labelIcon = QtWidgets.QLabel()
            labelIcon.setPixmap(icon)

            # Determine icon alignment.
            # If there is no message, it should align top
            # If no line breaks, it should align center.
            # With line breaks, it should align top.
            if message is None:
                iconAlignment = QtCore.Qt.AlignTop
            elif "\n" in message:
                iconAlignment = QtCore.Qt.AlignTop
            else:
                iconAlignment = QtCore.Qt.AlignVCenter

            # Add icon to layout
            self.layout().addWidget(labelIcon, 0, 0, iconAlignment)

        if message is not None:
            self.label = QtWidgets.QLabel(message)
            self.label.setWordWrap(True)
            self.layout().addWidget(self.label, 0, 1)

        if closable:
            self._addCloseButton()

        # raise the widget and adjust its size to the minimum
        self.raise_()
        self.adjustSize()

        self.corner = corner
        self.margin = margin

        geo = self.geometry()
        # now the widget should have the correct size hints, let's move it to the
        # right place
        if corner == QtCore.Qt.TopLeftCorner:
            geo.moveTopLeft(parentRect.topLeft() + QtCore.QPoint(margin, margin))
        elif corner == QtCore.Qt.TopRightCorner:
            geo.moveTopRight(parentRect.topRight() + QtCore.QPoint(-margin, margin))
        elif corner == QtCore.Qt.BottomRightCorner:
            geo.moveBottomRight(
                parentRect.bottomRight() + QtCore.QPoint(-margin, -margin)
            )
        else:
            geo.moveBottomLeft(parentRect.bottomLeft() + QtCore.QPoint(margin, -margin))

        self.setGeometry(geo)

    def show_(self, timeout=5000, toGeom=None, fromGeom=None):
        if not self.timer.isActive():
            self.timer.setInterval(timeout)
            self.timer.start()
        if not self.isShown:
            self.show()
            self.opacityAni.start()
            self.isShown = True
