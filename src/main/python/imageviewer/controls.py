
from collections import namedtuple

from PySide2 import QtCore, QtGui, QtWidgets

from base import config, ctx

from .colormenu import ColorMenu


class ImageController:
    '''
    This class implements the toolbar buttons
    and file menu options for an image editor
    '''

    def __init__(self, parent):

        self.parent = parent

        # Toolbar
        self.toolbar = QtWidgets.QToolBar('Image Controls')

        # Color palette button
        self.colorButton = QtWidgets.QToolButton(self.parent)
        self.colorButton.setDefaultAction(
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_palette.png'))))
        self.colorButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Color palette popup menu
        self._colorMenu = ColorMenu(config.colors)
        self._colorMenu.colorChanged.connect(self._penColorChanged)   

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)

        # Single-selection buttons -- only one can be selected at a time
        selectionActions = [
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_hand.png'))),
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_zoom.png'))),
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_oval.png'))),
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_rect.png'))),
            ColorableAction(self.parent, QtGui.QPixmap(ctx.get_resource('icons/ic_line.png'))),
        ]
        self.selectionActions = SingleSelectionGroup(selectionActions)
        self.selectionActions.itemChanged.connect(self._selectionActionChanged)

        # Add buttons to toolbar
        self.toolbar.addWidget(self.colorButton)
        self.toolbar.addActions(self.selectionActions.items)
        
        # Trigger the color menu signal to recolor necessary toolbar icons
        self._colorMenu.emitActiveColor()

    @QtCore.Slot(QtGui.QColor)
    def _penColorChanged(self, qcolor):
        self.colorButton.actions()[0].recolor(qcolor)
        print(f'Color changed to {qcolor}')

    @QtCore.Slot(QtWidgets.QAction)
    def _selectionActionChanged(self, action):
        print('Selection action changed')


class ColorableAction(QtWidgets.QAction):
    '''
    An action whose icon can be re-colored with a mask.
    Instance also contains information about what kind of drawing
    it might perform
    '''
    def __init__(self, parent, mask: QtGui.QPixmap):
        super().__init__(parent)
        self.mask = mask
        self.setIcon(mask)

    def recolor(self, color: QtGui.QColor):
        self.setIcon(ColorMenu.maskedIcon(color, self.mask))


class SingleSelectionGroup(QtCore.QObject):
    '''
    Manages a group of checkable objects of which only one can
    be checked at a time. Only tested with QActions so far.
    
    Items must have property `checked` and `checkable`.
    Items must have signal `triggered`.
    '''

    itemChanged = QtCore.Signal(QtCore.QObject)
    
    def __init__(self, items, startIndex=0):

        # Initialize signals
        super().__init__()

        # Store checkable items
        self._items = items

        # Ensure each item is checkable and currently unchecked
        for item in items:
            item.setCheckable(True)
            item.setChecked(False)
            item.triggered.connect(self._handleItemTriggered)

        # Set checked on one item to start
        self._activeIndex = startIndex
        self._items[startIndex].setChecked(True)

    @property
    def items(self):
        '''
        Read only property for all items in group
        '''
        return self._items

    def _handleItemTriggered(self, checked):

        # If we tried to uncheck an item, don't allow it
        if checked is False:
            self._items[self._activeIndex].setChecked(True)
            return

        # Uncheck the previously active index
        self._items[self._activeIndex].setChecked(False)

        # Find the new active item, change the active index,
        # and emit the item
        for i,item in enumerate(self._items):
            if item.isChecked():
                self._activeIndex = i
                self.itemChanged.emit(item)
                return
