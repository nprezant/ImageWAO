'''
Custom cursors used in the image editor window
'''

from PySide2 import QtGui

from base import ctx

class Cursors:
    eraser = QtGui.QCursor(QtGui.QPixmap(ctx.get_resource('icons/ic_eraser.png')))
    zoom = QtGui.QCursor(QtGui.QPixmap(ctx.get_resource('icons/ic_zoom.png')))
