
from collections import namedtuple

from PySide2 import QtCore, QtGui, QtWidgets

from base import config, ctx

from .colormenu import ColorMenu, ColorableAction
from .widthmenu import WidthMenu


class ImageController(QtCore.QObject):
    '''
    This class implements the toolbar buttons
    and file menu options for an image editor
    '''

    widthChanged = QtCore.Signal(int)
    colorChanged = QtCore.Signal(QtGui.QColor)
    mouseActionChanged = QtCore.Signal(QtWidgets.QAction)

    def __init__(self, parent, selectionActions):

        super().__init__()
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
        self._colorMenu.colorChanged.connect(self._colorChanged)   

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)

        # Width button
        self.widthButton = QtWidgets.QToolButton(self.parent)
        self.widthButton.setDefaultAction(
            ColorableAction(self.parent, ctx.defaultDockIcon))
        self.widthButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Width button popup menu
        self._widthMenu = WidthMenu(config.drawingWidths, config.defaultWidth)
        self._widthMenu.widthChanged.connect(self.widthChanged.emit)

        # Assign width menu to width button
        self.widthButton.setMenu(self._widthMenu)

        # Single-selection buttons -- only one can be selected at a time
        self.mouseActions = SingleSelectionGroup(selectionActions)
        self.mouseActions.itemChanged.connect(self.mouseActionChanged.emit)

        # Add buttons to toolbar
        self.toolbar.addWidget(self.colorButton)
        self.toolbar.addWidget(self.widthButton)
        self.toolbar.addActions(self.mouseActions.items)
        
        # Trigger the color menu signal to recolor necessary toolbar icons
        self._colorMenu.emitActiveColor()

    @property
    def activeMouseAction(self):
        return self.mouseActions.activeItem

    @QtCore.Slot(QtGui.QColor)
    def _colorChanged(self, qcolor):

        # Re-color the color button icon
        self.colorButton.actions()[0].recolor(qcolor)
        
        # Bubble up color
        self.colorChanged.emit(qcolor)

    def sendSignals(self):
        '''
        Sends the signals in this object.
        This can be useful for initializing Gui colors once
        slots are connected to these signals.
        '''
        self._colorMenu.emitActiveColor()
        self._widthMenu.emitActiveWidth()


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
        self.activeItem.setChecked(True)

    @property
    def items(self):
        '''
        Read only property for all items in group
        '''
        return self._items

    @property
    def activeItem(self):
        return self._items[self._activeIndex]

    def _handleItemTriggered(self, checked):

        # If we tried to uncheck an item, don't allow it
        if checked is False:
            self.activeItem.setChecked(True)
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
