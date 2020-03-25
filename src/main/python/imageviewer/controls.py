
from collections import namedtuple

from PySide2 import QtCore, QtGui, QtWidgets

from base import config, ctx
from ui import SingleUseAction

from .menus import ColorMenu, ColorableAction, WidthMenu


class ImageController(QtCore.QObject):
    '''
    This class implements the toolbar buttons
    and file menu options for an image editor
    '''

    widthChanged = QtCore.Signal(int)
    colorChanged = QtCore.Signal(QtGui.QColor)
    mouseActionChanged = QtCore.Signal(QtWidgets.QAction)
    zoomToFitRequested = QtCore.Signal()

    def __init__(self, parent, selectionActions):

        super().__init__(parent)

        # Toolbar
        self.toolbar = QtWidgets.QToolBar('Image Controls')

        # Color palette button
        self.colorButton = QtWidgets.QToolButton(self.parent())
        self.colorButton.setDefaultAction(
            ColorableAction(self.parent(), QtGui.QPixmap(ctx.get_resource('icons/ic_palette.png'))))
        self.colorButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Color palette popup menu
        self._colorMenu = ColorMenu(config.colors)
        self._colorMenu.colorChanged.connect(self._colorChanged)   

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)

        # Width button
        self.widthButton = QtWidgets.QToolButton(self.parent())
        self.widthButton.setDefaultAction(
            ColorableAction(self.parent(), ctx.defaultDockIcon))
        self.widthButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Width button popup menu
        self._widthMenu = WidthMenu(config.drawingWidths, config.defaultWidth)
        self._widthMenu.widthChanged.connect(self.widthChanged.emit)

        # Assign width menu to width button
        self.widthButton.setMenu(self._widthMenu)

        # Fit to screen button
        _zoomAct = QtWidgets.QAction('Zoom to fit', self.parent())
        _zoomAct.setIcon(QtGui.QIcon(ctx.get_resource('icons/ic_fitscreen.png')))
        self.zoomToFitButton = QtWidgets.QToolButton(self.parent())
        self.zoomToFitButton.setDefaultAction(_zoomAct)
        self.zoomToFitButton.triggered.connect(lambda *args: self.zoomToFitRequested.emit())

        # Single-selection buttons -- only one can be selected at a time
        self.mouseActions = SingleSelectionGroup(selectionActions)
        self.mouseActions.itemChanged.connect(self.mouseActionChanged.emit)

        # Add buttons to toolbar
        self.toolbar.addWidget(self.colorButton)
        self.toolbar.addWidget(self.widthButton)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.mouseActions.items)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.zoomToFitButton)
        
        # Trigger the color menu signal to recolor necessary toolbar icons
        self._colorMenu.emitActiveColor()

        # We want to know when the toolbutton is double clicked or single clicked.
        # We only want to know this for toolbuttons that are using SingleUseActions,
        # so we can install an event filter on these buttons to intercept within
        # this class.
        for button in self.toolbar.findChildren(QtWidgets.QToolButton):
            if isinstance(button.defaultAction(), SingleUseAction):
                button.installEventFilter(self)

        # Must track the last mouse event so we can determine whether tool buttons
        # are single or multi-use.
        self._lastMouseEvent = None
        self._mouseSingleUse = True

        # In order for us to know when an escape key event occurs, we need to filter events
        # on the widgets that this controller serves.
        if isinstance(self.parent(), QtWidgets.QGraphicsView):
            # Scene gets key events in a QGraphicsView
            self._parentEventWidget = self.parent().scene()
        else:
            self._parentEventWidget = self.parent()
        self._parentEventWidget.installEventFilter(self)

    def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):
        '''
        Sets whether a tool button is single use or multi-use based on
        whether the user clicked or double-clicked.

        Also checks whether that single use has been used up on the parent,
        and if so changes the active action.

        Order of events is important:
        Click:
            MouseButtonPress
            Paint
            MouseButtonRelease

        DoubleClick:
            MouseButtonPress
            Paint
            MouseButtonRelease
            ...
            MouseButtonDblClick
            Paint
            MouseButtonRelease
        '''
        if isinstance(watched, QtWidgets.QToolButton):
            if isinstance(watched.defaultAction(), SingleUseAction):

                # Set as multi use if the last mouse event was a double click ONLY
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if self._lastMouseEvent == QtCore.QEvent.MouseButtonDblClick:
                        self._mouseSingleUse = False
                    else:
                        self._mouseSingleUse = True
                    self._lastMouseEvent = QtCore.QEvent.MouseButtonRelease      
              
                elif event.type() == QtCore.QEvent.MouseButtonDblClick:
                    self._lastMouseEvent = QtCore.QEvent.MouseButtonDblClick

                elif event.type() == QtCore.QEvent.MouseButtonPress:
                    self._lastMouseEvent = QtCore.QEvent.MouseButtonPress

        # If we are pressing the escape key we should return to the default
        # active item
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == int(QtCore.Qt.Key_Escape):
                self.mouseActions.resetActiveItem()

        return super().eventFilter(watched, event)

    @QtCore.Slot()
    def mouseActionUsed(self):
        '''
        Use this slot to inform the controller that the mouse action
        was used and to update the active toolbuttons accordingly.
        This depends on whether the mouse action was set to single or
        multi use.
        '''
        if self._mouseSingleUse:
            self.mouseActions.resetActiveItem()

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
    
    def __init__(self, items, defaultIndex=0):

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
        self._defaultIndex = defaultIndex
        self._activeIndex = self._defaultIndex
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

    def resetActiveItem(self):
        '''
        Resets the active item to the default item specified
        by `_defaultIndex`.
        '''
        self._items[self._defaultIndex].trigger()

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
