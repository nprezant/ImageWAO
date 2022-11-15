"""
Custom button implementations.
"""

from PySide6 import QtGui, QtWidgets


class SingleUseAction(QtGui.QAction):
    """
    Same as a normal QAction, but will note whether the action is intended
    for single use or multiple uses.

    This flag must be set manually through `setSingleUse`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isSingleUse = True

    def isSingleUse(self):
        return self._isSingleUse

    def setSingleUse(self, value):
        self._isSingleUse = value


class SingleUseToolButton(QtWidgets.QToolButton):
    """
    Same as a normal QToolButton, but will note whether the button was pressed
    with the intent of a single use or multiple uses.

    A double click event will result in the single use flag being turned off.
    All other methods of triggering will result in the single use flag turned on.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._isSingleUse = True

    def isSingleUse(self):
        return self._isSingleUse

    def setSingleUse(self, value):
        self._isSingleUse = value

    def mouseDoubleClickEvent(self, ev: QtGui.QMouseEvent):
        self.setSingleUse(False)
        super().mouseDoubleClickEvent(ev)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent):
        self.setSingleUse(True)
        return super().mouseReleaseEvent(ev)
