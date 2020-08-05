from enum import Enum

from PySide2 import QtCore, QtGui, QtWidgets

from base import config, ctx

from .menus import ColorMenu, ColorableAction, WidthMenu


class ToolType(Enum):
    Default = 0
    HandTool = 1
    ZoomTool = 2
    OvalShape = 3
    RectangleShape = 4
    LineShape = 5
    Eraser = 6


class MouseToolAction(ColorableAction):
    """
    An action associated with a specific mouse tool use
    """

    def __init__(self, tooltype, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tooltype = tooltype

        # Convenience -- if this is a "shape" tool
        if "shape" in tooltype.name.lower():
            self.isShapeTool = True
        else:
            self.isShapeTool = False


def createSelectionActions(parent):
    """
    Convienence method for separating out where the selection actions are
    defined.
    """

    # Tool definitions
    handTool = MouseToolAction(
        ToolType.HandTool,
        QtGui.QPixmap(ctx.get_resource("icons/hand.png")),
        "Hand tool (ESC)",
        parent,
    )
    zoomTool = MouseToolAction(
        ToolType.ZoomTool,
        QtGui.QPixmap(ctx.get_resource("icons/zoom.png")),
        "Zoom tool (Z)",
        parent,
    )
    ovalTool = MouseToolAction(
        ToolType.OvalShape,
        QtGui.QPixmap(ctx.get_resource("icons/oval.png")),
        "Oval shape (O)",
        parent,
    )
    rectTool = MouseToolAction(
        ToolType.RectangleShape,
        QtGui.QPixmap(ctx.get_resource("icons/rect.png")),
        "Rectangle shape (R)",
        parent,
    )
    lineTool = MouseToolAction(
        ToolType.LineShape,
        QtGui.QPixmap(ctx.get_resource("icons/line.png")),
        "Line shape (L)",
        parent,
    )
    erasTool = MouseToolAction(
        ToolType.Eraser,
        QtGui.QPixmap(ctx.get_resource("icons/eraser.png")),
        "Eraser (E)",
        parent,
    )

    # Key sequences
    handTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape))
    zoomTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Z))
    ovalTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_O))
    rectTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_R))
    lineTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_L))
    erasTool.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_E))

    return [handTool, zoomTool, ovalTool, rectTool, lineTool, erasTool]


class ImageController(QtCore.QObject):
    """
    This class implements the toolbar buttons
    and file menu options for an image editor
    """

    widthChanged = QtCore.Signal(int)
    colorChanged = QtCore.Signal(QtGui.QColor)
    mouseActionChanged = QtCore.Signal(QtWidgets.QAction)
    zoomToFitRequested = QtCore.Signal()
    zoomInRequested = QtCore.Signal()
    zoomOutRequested = QtCore.Signal()

    def __init__(self, parent):

        super().__init__(parent)

        # Toolbar
        self.toolbar = QtWidgets.QToolBar("Image Controls")

        # Color palette button
        self.colorButton = QtWidgets.QToolButton(self.parent())
        self.colorButton.setDefaultAction(
            ColorableAction(
                QtGui.QPixmap(ctx.get_resource("icons/palette.png")),
                "Change color",
                self.parent(),
            )
        )
        self.colorButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Color palette popup menu
        self._colorMenu = ColorMenu(config.colors)
        self._colorMenu.colorChanged.connect(self._colorChanged)

        # Assign menu to button & button to toolbar
        self.colorButton.setMenu(self._colorMenu)

        # Width button
        self.widthButton = QtWidgets.QToolButton(self.parent())
        self.widthButton.setDefaultAction(
            ColorableAction(ctx.defaultDockIcon, "Change line width", self.parent())
        )
        self.widthButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # Width button popup menu
        self._widthMenu = WidthMenu(config.drawingWidths, config.defaultWidth)
        self._widthMenu.widthChanged.connect(self.widthChanged.emit)

        # Assign width menu to width button
        self.widthButton.setMenu(self._widthMenu)

        # Fit to screen button
        _zoomAct = QtWidgets.QAction("Zoom to fit (SPACE)", self.parent())
        _zoomAct.setIcon(QtGui.QIcon(ctx.get_resource("icons/fitscreen.png")))
        _zoomAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space))
        self.zoomToFitButton = QtWidgets.QToolButton(self.parent())
        self.zoomToFitButton.setDefaultAction(_zoomAct)
        self.zoomToFitButton.triggered.connect(
            lambda *args: self.zoomToFitRequested.emit()
        )

        # Zoom in button
        _zoomInAct = QtWidgets.QAction("Zoom in (+)", self.parent())
        _zoomInAct.setIcon(QtGui.QIcon(ctx.get_resource("icons/zoomin.png")))
        # Shortcuts
        self._plusShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Plus), self.parent()
        )
        self._equalShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Equal), self.parent()
        )
        self._plusShortcut.activated.connect(_zoomInAct.trigger)
        self._equalShortcut.activated.connect(_zoomInAct.trigger)
        # Button
        self.zoomInButton = QtWidgets.QToolButton(self.parent())
        self.zoomInButton.setDefaultAction(_zoomInAct)
        self.zoomInButton.triggered.connect(lambda *args: self.zoomInRequested.emit())

        # Zoom out button
        _zoomOutAct = QtWidgets.QAction("Zoom out (-)", self.parent())
        _zoomOutAct.setIcon(QtGui.QIcon(ctx.get_resource("icons/zoomout.png")))
        # Shortcuts
        self._minusShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_Minus), self.parent()
        )
        self._hyphenShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key_hyphen), self.parent()
        )
        self._minusShortcut.activated.connect(_zoomOutAct.trigger)
        self._hyphenShortcut.activated.connect(_zoomOutAct.trigger)
        # Button
        self.zoomOutButton = QtWidgets.QToolButton(self.parent())
        self.zoomOutButton.setDefaultAction(_zoomOutAct)
        self.zoomOutButton.triggered.connect(lambda *args: self.zoomOutRequested.emit())

        # Single-selection buttons -- only one can be selected at a time
        self.mouseActions = SingleSelectionGroup(createSelectionActions(self))
        self.mouseActions.itemChanged.connect(self.mouseActionChanged.emit)

        # Add buttons to toolbar
        self.toolbar.addWidget(self.colorButton)
        self.toolbar.addWidget(self.widthButton)
        self.toolbar.addSeparator()
        self.toolbar.addActions(self.mouseActions.items)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.zoomToFitButton)
        self.toolbar.addWidget(self.zoomOutButton)
        self.toolbar.addWidget(self.zoomInButton)

        # Trigger the color menu signal to recolor necessary toolbar icons
        self._colorMenu.emitActiveColor()

        # We want to know when the toolbutton is double clicked or single clicked.
        # We only want to know this for toolbuttons that are using SingleUseActions,
        # so we can install an event filter on these buttons to intercept within
        # this class.
        for button in self.toolbar.findChildren(QtWidgets.QToolButton):
            if isinstance(button.defaultAction(), MouseToolAction):
                button.installEventFilter(self)

        # Must track the last mouse event so we can determine whether tool buttons
        # are single or multi-use.
        self._lastMouseEvent = None
        self._mouseSingleUse = True

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent):
        """
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
        """
        if isinstance(watched, QtWidgets.QToolButton):
            if isinstance(watched.defaultAction(), MouseToolAction):

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

        return super().eventFilter(watched, event)

    @QtCore.Slot()
    def mouseActionUsed(self):
        """
        Use this slot to inform the controller that the mouse action
        was used and to update the active toolbuttons accordingly.
        This depends on whether the mouse action was set to single or
        multi use.
        """
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
        """
        Sends the signals in this object.
        This can be useful for initializing Gui colors once
        slots are connected to these signals.
        """
        self._colorMenu.emitActiveColor()
        self._widthMenu.emitActiveWidth()


class SingleSelectionGroup(QtCore.QObject):
    """
    Manages a group of checkable objects of which only one can
    be checked at a time. Only tested with QActions so far.

    Items must have property `checked` and `checkable`.
    Items must have signal `triggered`.
    """

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
        """
        Read only property for all items in group
        """
        return self._items

    @property
    def activeItem(self):
        return self._items[self._activeIndex]

    def resetActiveItem(self):
        """
        Resets the active item to the default item specified
        by `_defaultIndex`.
        """
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
        for i, item in enumerate(self._items):
            if item.isChecked():
                self._activeIndex = i
                self.itemChanged.emit(item)
                return
