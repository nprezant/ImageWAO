
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

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)

        # Drawing buttons
        self.ovalButton = QtWidgets.QToolButton(self)
        self.rectButton = QtWidgets.QToolButton(self)
        self.lineButton = QtWidgets.QToolButton(self)

        # Drawing icn masks
        self.ovalMask = QtGui.QPixmap(ctx.get_resource('icons/ic_oval.png'))
        self.rectMask = QtGui.QPixmap(ctx.get_resource('icons/ic_rect.png'))
        self.lineMask = QtGui.QPixmap(ctx.get_resource('icons/ic_line.png'))

        # Add buttons to toolbar
        self.toolbar.addWidget(self.colorButton)
        self.toolbar.addWidget(self.ovalButton)
        self.toolbar.addWidget(self.rectButton)
        self.toolbar.addWidget(self.lineButton)
        
        self._colorMenu.reset() # Nesessary to catch the signal for the default color

    @QtCore.Slot(QtGui.QColor)
    def _penColorChanged(self, qcolor):
        self.colorButton.setIcon(ColorMenu.maskedIcon(qcolor, self.paletteMask))
        self.ovalButton.setIcon(ColorMenu.maskedIcon(qcolor, self.ovalMask))
        self.rectButton.setIcon(ColorMenu.maskedIcon(qcolor, self.rectMask))
        self.lineButton.setIcon(ColorMenu.maskedIcon(qcolor, self.lineMask))
        print(f'Color changed to {qcolor}')
        

    