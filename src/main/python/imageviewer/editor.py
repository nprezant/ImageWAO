
from PySide2 import QtCore, QtGui, QtWidgets

from base import config

from .imageviewer2 import QImageViewer
from .palette import QPaletteIcon



class QImageEditor(QImageViewer):

    def __init__(self):
        super().__init__()

        self.toolbar = QtWidgets.QToolBar('Editing')
        self._createToolbar()

    def _createToolbar(self):

        # Color palette buttons
        colorButton = QtWidgets.QToolButton(self)
        colorButton.setText('Brush Color')
        colorButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self._colorMenu = QtWidgets.QMenu()
        self._colorActions = QPaletteIcon.createColorActions(config.colors)
        for a in self._colorActions:
            self._colorMenu.addAction(a)

        colorButton.setMenu(self._colorMenu)
        self.toolbar.addWidget(colorButton)
        

    