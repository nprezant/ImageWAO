'''
Custom cursors used in the image editor window
'''

from PySide2 import QtGui

from base import ctx

class Cursors:

    _eraserPixmap = QtGui.QPixmap(ctx.get_resource('icons/ic_eraser.png'))
    _zoomPixmap = QtGui.QPixmap(ctx.get_resource('icons/ic_zoom.png'))

    eraser = QtGui.QCursor(_eraserPixmap, hotx=0, hoty=_eraserPixmap.height())
    zoom = QtGui.QCursor(_zoomPixmap, hotx=0, hoty=0)
