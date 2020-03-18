
from PySide2 import QtGui, QtWidgets

def setPlainTextEditHeight(ptxt: QtWidgets.QPlainTextEdit, nRows: int):
    '''
    Sets the height of a plain text edit box to a set number of rows.
    '''
    pdoc = ptxt.document()
    fm = QtGui.QFontMetrics(pdoc.defaultFont())
    margins = ptxt.contentsMargins()
    rowHeight = fm.lineSpacing()
    height = (
        rowHeight * nRows
        + 2*(pdoc.documentMargin() + ptxt.frameWidth())
        + margins.top() + margins.bottom())
    ptxt.setFixedHeight(height)
