
import json
from enum import Enum

from PySide2 import QtCore, QtGui, QtWidgets

from .imageviewer2 import QImageViewer
from .controls import ImageController, ColorableAction, ctx

eraserCursor = QtGui.QCursor(QtGui.QPixmap(ctx.get_resource('icons/ic_eraser.png')))

class ToolType(Enum):
    Default = 0
    HandTool = 1
    ZoomTool = 2
    OvalShape = 3
    RectangleShape = 4
    LineShape = 5
    Eraser = 6


class QImageEditor(QImageViewer):

    # Emits signal with a list of encoded items
    # When a new item is drawn or removed
    drawnItemsChanged = QtCore.Signal(list)

    def __init__(self):
        super().__init__()

        # Editor can have several selector states.
        # Normal (default -- whatever the QImageViewer does)
        # Zoom (User can zoom with the bounding rubber band box)
        # Drawing (User can draw on image with specified shape)

        # Controller (Toolbar, file menu, etc.)
        selectionActions = [
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_hand.png')), ToolType.HandTool),
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_zoom.png')), ToolType.ZoomTool),
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_oval.png')), ToolType.OvalShape),
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_rect.png')), ToolType.RectangleShape),
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_line.png')), ToolType.LineShape),
            MouseToolAction(self, QtGui.QPixmap(ctx.get_resource('icons/ic_eraser.png')), ToolType.Eraser),
        ]
        self.controller = ImageController(self, selectionActions)

        # Drawing pen
        self._pen = QtGui.QPen()
        self._pen.setWidth(30)

        # Connections
        self.controller.colorChanged.connect(self._updatePenColor)
        self.controller.mouseActionChanged.connect(self._mouseActionChanged)
        self.controller.sendSignals()

        # Drawing variables
        self._drawnItems = []
        self._dynamicallyDrawnItem = None
        self._erasing = False

        # TODO: Create a way to save/load drawn items.
        # Eventually these drawn items must be saved as pixmaps,
        # But before that it would be nice to have a simple save/load operation
        # just for the drawn items. Then, those can be saved to a seperate file,
        # and just those items can be loaded in when we look at someone's transects.
        #
        # Additionally, we'll be able to show a QListView of these items, and perhaps
        # include some nice select & delete operations to go along with it.
        # 
        # On top of that, when we are comparing one person's transects to another
        # person's, we can choose whose *counts* (including markup) to look at. 
        
    @property
    def toolbar(self):
        '''
        Alias for self.controller.toolbar
        '''
        return self.controller.toolbar

    @property
    def mouseAction(self):
        '''
        Alias for self.controller.activeMouseAction
        '''
        return self.controller.activeMouseAction

    def setImage(self, image):
        '''
        Re-implement to ensure that drawn items are 
        cleared when a new image is set
        '''
        self._clearDrawnItems()
        super().setImage(image)

    @QtCore.Slot(QtGui.QColor)
    def _updatePenColor(self, qcolor):
        '''
        Set internal pen color, used for new drawings
        '''
        self._pen.setColor(qcolor)

    @QtCore.Slot(QtWidgets.QAction)
    def _mouseActionChanged(self, action):
        '''
        When the mouse action changes, we need to update
        the cursor icon.
        '''
        if action.isShapeTool:
            self.setCursor(QtCore.Qt.CrossCursor)
        elif action.tooltype == ToolType.Eraser:
            self.setCursor(eraserCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def _emitDrawnItems(self):

        # Need to make a list of encoded items
        encoded = []

        for item in self._drawnItems:

            # Encoded data differs depending on item type
            # Need to save as much data as necessary to re-create item
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                name = 'Rect'
                rect = item.rect()
                args = [rect.x(), rect.y(), rect.width(), rect.height()]

            elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
                name = 'Ellipse'
                rect = item.rect()
                args = [rect.x(), rect.y(), rect.width(), rect.height()]

            elif isinstance(item, QtWidgets.QGraphicsLineItem):
                name = 'Line'
                line = item.line()
                args = [line.x1(), line.y1(), line.x2(), line.y2()]

            else:
                print(f'Unrecognized item: {item}')
                continue

            # All graphics items have associated pens
            if isinstance(item, QtWidgets.QGraphicsItem):
                pen = item.pen()
                penColor = pen.color().name() # In #RRGGBB format
                penWidth = pen.width()

            encoded.append([name, args, penColor, penWidth])

        serialized = json.dumps(encoded)
        self.drawnItemsChanged.emit(serialized)

    def readSerializedDrawnItems(self, serialized):
        '''
        Reads serialized data about drawn items into
        itself the current scene.
        '''
        data = json.loads(serialized)
        for dataItem in data:

            # TODO: Error checking -- enough data in list?
            # correct data in list?
            name = dataItem[0]
            args = dataItem[1]
            penColor = dataItem[2]
            penWidth = dataItem[3]

            # Setup pen
            pen = QtGui.QPen(penColor) # Does this color need to be a QColor?
            pen.setWidth(penWidth)

            if name == 'Rect':
                rect = QtCore.QRectF(*args)
                item = self.scene.addRect(rect, pen)
            elif name == 'Ellipse':
                rect = QtCore.QRectF(*args)
                item = self.scene.addEllipse(rect, pen)
            elif name == 'Line':
                line = QtCore.QLineF(*args)
                item = self.scene.addLine(line, pen)

            self._drawnItems.append(item)

    def _clearDrawnItems(self):
        for item in self._drawnItems:
            self.scene.removeItem(item)

        self._drawnItems.clear()

    def _removeDrawnItemsUnderPoint(self, point:QtCore.QPointF):
        for item in self._drawnItems:
            if item.contains(point):
                self.scene.removeItem(item)
                self._drawnItems.remove(item)

    def mousePressEvent(self, event):

        # Sometimes we want the default handler
        if (
            self.scenePixmap() is None # No image loaded
            or self.mouseAction.tooltype == ToolType.HandTool
        ):
            super().mousePressEvent(event)
            return

        # Shape tool handler
        if self.mouseAction.isShapeTool:

            # Draw if this is the left button
            if event.button() == QtCore.Qt.LeftButton:

                # Don't start drawing unless the pixmap is under the
                # mouse in the scene
                if not self.scenePixmap().isUnderMouse():
                    super().mousePressEvent(event)
                    return
                else:
                    pos = self.mapToScene(event.pos())
                    initialRect = QtCore.QRectF(pos.x(), pos.y(), 1, 1)
                    
                if self.mouseAction.tooltype == ToolType.OvalShape:
                    self._dynamicallyDrawnItem = self.scene.addEllipse(initialRect, self._pen)
                elif self.mouseAction.tooltype == ToolType.RectangleShape:
                    self._dynamicallyDrawnItem = self.scene.addRect(initialRect, self._pen)
                elif self.mouseAction.tooltype == ToolType.LineShape:
                    line = QtCore.QLineF(
                        pos.x(), pos.y(),
                        pos.x()+1, pos.y()+1)
                    self._dynamicallyDrawnItem = self.scene.addLine(line, self._pen)

            # Erase if this is the right button
            elif event.button() == QtCore.Qt.RightButton:
                self._erasing = True
                self._removeDrawnItemsUnderPoint(self.mapToScene(event.pos()))

        elif self.mouseAction.tooltype == ToolType.Eraser:
            # When the mouse moves, if the mouse was pressed with this tool,
            # we need to know that we are still erasing
            self._erasing = True
            self._removeDrawnItemsUnderPoint(self.mapToScene(event.pos()))
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        # Update dynamically drawn object if it exists
        if self._dynamicallyDrawnItem is not None:

            # Current mouse position
            pos = self.mapToScene(event.pos())

            # Some shapes use rectangles
            if self.mouseAction.tooltype in (ToolType.OvalShape, ToolType.RectangleShape):
                rect = self._dynamicallyDrawnItem.rect()
                rect.setBottomRight(QtCore.QPointF(pos.x(), pos.y()))
                self._dynamicallyDrawnItem.setRect(rect)

            # Some shapes use lines
            elif self.mouseAction.tooltype == ToolType.LineShape:
                line = self._dynamicallyDrawnItem.line()
                line.setP2(QtCore.QPointF(pos.x(), pos.y()))
                self._dynamicallyDrawnItem.setLine(line)

        # If we are erasing currently, we need to remove items
        elif self._erasing:
            self._removeDrawnItemsUnderPoint(self.mapToScene(event.pos()))

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        # Save the most recent drawn object if it exists
        if self._dynamicallyDrawnItem is not None:

            # Only save is shape is a valid size
            valid = False
            minLength = self._pen.width()

            # Some shapes use rectangles
            if self.mouseAction.tooltype in (ToolType.OvalShape, ToolType.RectangleShape):
                rect = self._dynamicallyDrawnItem.rect()

                # Absolute value required because items have negative
                # width/height when they are drawn from right to left
                width = abs(rect.width())
                height = abs(rect.height())

                if width > minLength and height > minLength:
                    valid = True                

            # Some shapes use lines
            elif self.mouseAction.tooltype == ToolType.LineShape:

                if self._dynamicallyDrawnItem.line().length() > minLength:
                    valid = True

            # Only save if the shape is a valid size
            if valid:
                self._drawnItems.append(self._dynamicallyDrawnItem)
                self._emitDrawnItems()
            else:
                self.scene.removeItem(self._dynamicallyDrawnItem)

            # Reset object handle
            self._dynamicallyDrawnItem = None

        # If we just erased something, let the world know
        elif self._erasing:
            self._erasing = False
            self._emitDrawnItems()

        else:
            super().mouseReleaseEvent(event)
        

class MouseToolAction(ColorableAction):
    '''
    An action associated with a specific mouse tool use
    '''

    def __init__(self, parent, mask, tooltype=ToolType.Default):
        super().__init__(parent, mask)

        self.tooltype = tooltype

        # Convenience -- if this is a "shape" tool
        if 'shape' in tooltype.name.lower():
            self.isShapeTool = True
        else:
            self.isShapeTool = False
