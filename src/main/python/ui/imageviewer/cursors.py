"""
Custom cursors used in the image editor window
"""

from PySide6 import QtGui

from base import ctx


class Cursors:

    _eraserPixmap = QtGui.QPixmap(ctx.get_resource("icons/eraser.png"))
    _zoomPixmap = QtGui.QPixmap(ctx.get_resource("icons/zoom.png"))

    eraser = QtGui.QCursor(_eraserPixmap, 0, _eraserPixmap.height())
    zoom = QtGui.QCursor(_zoomPixmap, 0, 0)
