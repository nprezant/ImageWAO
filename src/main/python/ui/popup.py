"""
Custom popup implementation with opacity tied into
the mouse cursor distance from it.
"""

from PySide2 import QtCore, QtWidgets

from tools import distanceToRect


class PopupFrame(QtWidgets.QFrame):

    popupHidden = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent)

        # The popup window will hide itself when the mouse moves this distance
        # away from the window
        self._hidePopupDistance = 50
        self._hidePersistantPopupDistance = 150
        self._fullOpacityMargin = 10
        self._extraAutoMargin = 0

        # Install an eventFilter so that we can track mouse positions
        # and hide the popup when the user doesn't mouse over it.
        # Mouse events exist in the viewport, if the parent has one.
        try:
            filterable = self.parent().viewport()
        except AttributeError:
            filterable = self.parent()
        finally:
            filterable.installEventFilter(self)

        # Setup the opacity effect
        self._opacityEffect = QtWidgets.QGraphicsOpacityEffect(opacity=1)
        self.setGraphicsEffect(self._opacityEffect)

        # Don't show on construction.
        # Parent must call "popup" to show
        self.hide()

        # Hide automatically by default.
        self._persistant = False

        # Mouse tracking state used to keep track of what the parent's
        # mouse tracking state was before we changed it.
        self._mouseTrackingState = False

    def popup(self, pos: QtCore.QPointF):
        """
        Show the Count Form as a popup window.
        Hide form if mouse does not immediately move it.
        """

        # Show
        self.setPersistance(False)
        self._autoPosition(pos)
        self.raise_()
        self.show()

        # Setup mouse tracking. This is required to receive mouse events
        # even when no mouse buttons are pressed.
        self._mouseTrackingState = self.parent().hasMouseTracking()
        self.parent().setMouseTracking(True)

    def _autoPosition(self, pos: QtCore.QPointF):
        """
        Automatically positions the widget. Sets position just outside of
        the fullOpacityMargin so the widget initializes as semi-transparent.
        Tries to place widget to the lower right of the position.
        """

        # Get sizes
        parentSize: QtCore.QSizeF = self.parent().size()
        size: QtCore.QSizeF = self.size()

        # Margin around rect. Increase the fullOpacityMargin so the widget
        # starts out semi-transparent.
        margin = self._fullOpacityMargin + self._extraAutoMargin

        # Update opacity to reflect new cursor distance from the widget
        self._updateDistanceOpacity((margin ** 2 + margin ** 2) ** (0.5))

        # Initialize fitting checks
        rightFit = False
        leftFit = False
        topFit = False
        bottomFit = False

        # Check if the widget could fit to the right of the position
        if pos.x() + margin + size.width() < parentSize.width():
            rightFit = True
        else:
            rightFit = False

        # Check if the widget could fit to the left of the position
        if pos.x() - margin - size.width() > 0:
            leftFit = True
        else:
            leftFit = False

        # Check if the widget could fit to the bottom of the position
        if pos.y() + margin + size.height() < parentSize.height():
            bottomFit = True
        else:
            bottomFit = False

        # Check if the widget could fit to the top of the position
        if pos.y() - margin - size.height() > 0:
            topFit = True
        else:
            topFit = False

        # Retreive geometry
        geo = self.geometry()

        # Favored position is below and to the right
        if (
            rightFit
            and bottomFit
            or rightFit
            and not topFit
            or not leftFit
            and not topFit
        ):
            geo.moveTopLeft(QtCore.QPoint(pos.x() + margin, pos.y() + margin))

        # Above to the right
        elif rightFit and topFit or not leftFit and topFit:
            geo.moveBottomLeft(QtCore.QPoint(pos.x() + margin, pos.y() - margin))

        # Below to the left
        elif leftFit and bottomFit or leftFit and not topFit:
            geo.moveTopRight(QtCore.QPoint(pos.x() - margin, pos.y() + margin))

        # Above to the left
        else:
            geo.moveBottomRight(QtCore.QPoint(pos.x() - margin, pos.y() - margin))

        # Assign newly positioned geometry
        self.setGeometry(geo)

    def hidePopup(self):
        """
        Hides the popup window.
        """

        if self.isHidden():
            return

        # Clean up parent mouse tracking state
        self.parent().setMouseTracking(self._mouseTrackingState)

        # Clean up persistance
        self._persistant = False

        # Emit a signal noting that the popup was hidden
        self.popupHidden.emit()

        self.hide()

    def setPersistance(self, value: bool):
        """
        Notes that this widget should persist regardless of
        mouse movement.
        """
        if value:
            self._persistant = True
            self._opacityEffect.setOpacity(1)
        else:
            self._persistant = False

    def isPersistant(self):
        return self._persistant

    def eventFilter(self, source: QtCore.QObject, event: QtCore.QEvent):
        """
        Grabs mouse events from outside the widget
        """

        # If the user clicks outside of this widget, hide it.
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.hidePopup()

        # If the user moves the mouse outside of this widget,
        # determine whether we need to do anything about that.
        elif event.type() == QtCore.QEvent.MouseMove:

            # If we are not visible, no need to compute anything
            if self.isVisible() is False:
                pass

            else:
                # Compute distance to mouse cursor.
                d = distanceToRect(event.pos(), self.geometry())

                # Update opacity based on distance
                self._updateDistanceOpacity(d)

        return super().eventFilter(source, event)

    def _updateDistanceOpacity(self, d):
        """
        Updates the widget opacity and hidden status based on
        the cursor distance to the widget.
        """
        # The hiding distance changes depending
        if self.isPersistant():
            hideDistance = self._hidePersistantPopupDistance
        else:
            hideDistance = self._hidePopupDistance

        # If the cursor is too far away, hide the popup
        if d > hideDistance:
            self.hidePopup()

        # If the cursor is within a close margin, set 100% opacity
        elif d < self._fullOpacityMargin:
            self._opacityEffect.setOpacity(1)

        # If the cursor is some other distance, adjust the opacity
        else:
            opacity = 1 - (d - self._fullOpacityMargin) / (
                hideDistance - self._fullOpacityMargin
            )
            self._opacityEffect.setOpacity(opacity)

    def enterEvent(self, event: QtCore.QEvent):
        """
        When the mouse enters this widget, we need to note that
        the widget should persist until the user clicks elsewhere.
        """
        self.setPersistance(True)
