
from PySide2 import QtCore, QtGui, QtWidgets

from base import config, ctx

from .imageviewer2 import QImageViewer
from .palette import ColorMenu


class QImageEditor(QImageViewer):

    def __init__(self):
        super().__init__()

        # Editor can have several selector states.
        # Normal (default -- whatever the QImageViewer does)
        # Zoom (User can zoom with the bounding rubber band box)
        # Drawing (User can draw on image with specified shape)

        # Toolbar
        self.toolbar = QtWidgets.QToolBar('Editing')

        # Color palette button
        self.colorButton = QtWidgets.QToolButton(self)
        self.colorButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.paletteMask = QtGui.QPixmap(ctx.get_resource('icons/ic_palette.png'))

        # Color palette popup menu
        self._colorMenu = ColorMenu(config.colors)
        self._colorMenu.colorChanged.connect(self._penColorChanged)   
        self._colorMenu.reset() # Nesessary to catch the signal for the default color

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)
        self.toolbar.addWidget(self.colorButton)

    @QtCore.Slot(QtGui.QColor)
    def _penColorChanged(self, qcolor):
        self.colorButton.setIcon(ColorMenu.maskedIcon(qcolor, self.paletteMask))
        print(f'Color changed to {qcolor}')
        

    