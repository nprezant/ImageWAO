
from PySide2 import QtCore, QtGui, QtWidgets

from serializers import JSONDrawnItems
from ui import CountForm

import scenegraphics as sg

from .imageviewer import QImageViewer
from .controls import ImageController, ColorableAction, ctx, ToolType
from .cursors import Cursors
from .menus import ItemMenu


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
        self.controller = ImageController(self)

        # Drawing pen
        self._pen = QtGui.QPen()
        self._pen.setWidth(30)

        # Connections
        self.controller.colorChanged.connect(self._updatePenColor)
        self.controller.widthChanged.connect(self._updatePenWidth)
        self.controller.mouseActionChanged.connect(self._updateCursor)
        self.controller.zoomToFitRequested.connect(self.clearZoom)
        self.controller.zoomInRequested.connect(lambda: self.zoomIn(0.1))
        self.controller.zoomOutRequested.connect(lambda: self.zoomOut(0.1))
        self.controller.sendSignals()

        # Drawing variables
        self._dynamicallyDrawnItem = None
        self._erasing = False

        # Animal counting editor. When the counts form count changes,
        # the editor must update it's drawings.
        self._countForm = CountForm(self)
        self._countForm.countChanged.connect(self.itemCountsUpdated)

        # Required to propogate events to the drawing items
        # This is necessary for the drawn items to display their associated counts.
        self.setMouseTracking(True)

        # Modulator key tracking for viewport navigation
        self._ctrlPressed = False

        # Menu
        self.menu = ItemMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)
        
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

    @QtCore.Slot()
    def clear(self):
        '''
        Clears the image and the current drawings.
        '''
        self.scene().clear()

    @QtCore.Slot(QtGui.QImage, str)
    def setImage(self, image:QtGui.QImage, drawings:str):
        '''
        Re-implement to ensure that drawn items are 
        cleared when a new image is set, and to save
        the old image if necessary
        '''
        self.scene().clear() # We'll be redrawing the whole scene
        self._countForm.hidePopup() # Ensure popup is hidden
        super().setImage(image)

        # If we have drawings, redraw them
        if not drawings in (None, ''):
            self.readSerializedDrawnItems(drawings)

    @QtCore.Slot(QtGui.QColor)
    def _updatePenColor(self, qcolor):
        '''
        Set internal pen color, used for new drawings
        '''
        self._pen.setColor(qcolor)

    @QtCore.Slot(int)
    def _updatePenWidth(self, width):
        '''
        Set internal pen width, used for new drawings
        '''
        self._pen.setWidth(width)

    @QtCore.Slot(QtWidgets.QAction)
    def _updateCursor(self, action=None):
        '''
        Update the mouse cursor based on the currently
        active mouse action
        '''
        if self.mouseAction.isShapeTool:
            self.setCursor(QtCore.Qt.CrossCursor)
        elif self.mouseAction.tooltype == ToolType.Eraser:
            self.setCursor(Cursors.eraser)
        elif self.mouseAction.tooltype == ToolType.ZoomTool:
            self.setCursor(Cursors.zoom)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    @QtCore.Slot()
    def itemCountsUpdated(self):
        '''
        Since an item's counts were updated, emit the items.
        '''
        self._emitDrawnItems()

    @QtCore.Slot(QtCore.QPoint)
    def _customMenuRequested(self, pos:QtCore.QPoint):
        '''
        Open the context menu with the currently selected item.
        '''

        # The context menu is only accessible from the main mouse tool
        if not self.mouseAction.tooltype == ToolType.HandTool:
            return

        # Get the topmost item at this point and let the context 
        # menu know (if it is a scene counts item)
        item = self.itemAt(pos)
        if isinstance(item, sg.SceneCountsItemMixin):
            self.menu.addEditableItem(item, lambda *args: self._countForm.popup(item, pos), 'Edit counts')
            self.menu.addDeletableItem(item, lambda *args: self.scene().removeItem(item), 'Erase')

            # Show the menu
            self.menu.popup(self.mapToGlobal(pos))

    def _emitDrawnItems(self):
        '''
        Serialize drawn items into JSON format and
        emit via the drawnItemsChanged signal
        '''
        # Get each of the drawn items
        drawnItems = []
        for item in self.scene().items():
            if isinstance(item ,sg.SceneCountsItemMixin):
                drawnItems.append(item)

        serializer = JSONDrawnItems.loadDrawingData(drawnItems)
        self.drawnItemsChanged.emit(serializer.dumps())

    def readSerializedDrawnItems(self, serialized):
        '''
        Reads serialized data about drawn items into
        itself the current scene.
        '''
        serializer = JSONDrawnItems.loads(serialized)
        serializer.addToScene(self.scene())

    def _removeDrawnItemsUnderPoint(self, point:QtCore.QPointF):
        items = self.scene().items(point)
        for item in items:
            if isinstance(item, sg.SceneCountsItemMixin):
                self.scene().removeItem(item)

    def keyPressEvent(self, event:QtGui.QKeyEvent):
        '''
        Some keys are necessary to track for navigating the view
        with the mouse and keyboard.
        '''
        if event.key() == QtCore.Qt.Key_Control:
            self._ctrlPressed = True

            # If we are currently on the main mouse button, we should update the cursor
            # to let the user know that we can pan around now.
            if self.mouseAction.tooltype == ToolType.HandTool:
                self.setCursor(QtCore.Qt.OpenHandCursor)

        # Plus and equal keys are often in the same button
        if event.key() in (QtCore.Qt.Key_Plus, QtCore.Qt.Key_Equal):
            self.zoomIn(0.1)

        elif event.key() == QtCore.Qt.Key_Minus:
            self.zoomOut(0.1)

        # If the count form is shown, forward events there.
        if self._countForm.isVisible():
            self._countForm.keyPressEvent(event)

        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event:QtGui.QKeyEvent):
        '''
        Some keys are necessary to track for navigating the view
        with the mouse and keyboard.
        '''
        if event.key() == QtCore.Qt.Key_Control:
            self._ctrlPressed = False

            # If we just had the panning cursor up, we can't pan anymore and
            # should update the cursor to match.
            if self.cursor() == QtCore.Qt.OpenHandCursor:
                self.setCursor(QtCore.Qt.ArrowCursor)

        return super().keyReleaseEvent(event)

    def leaveEvent(self, event:QtCore.QEvent):
        '''
        When the mouse leaves the widget we reset modulator keys
        '''
        self._ctrlPressed = False

    def mousePressEvent(self, event):

        # Sometimes we want the default handler,
        # Like when no image is loaded.
        if not self.hasMainImage():
            pass

        # Standard hand tool allows selection rubber band with left
        # mouse button, or panning if the control key is pressed.
        # The context menu pops up with the right mouse button (handled
        # on mouse release)
        elif self.mouseAction.tooltype == ToolType.HandTool:
            if event.button() == QtCore.Qt.LeftButton:
                if self._ctrlPressed:
                    self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                else:
                    self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        # Zoom tool allows user to zoom in and out with 
        # a selection rubber band box. The release event takes
        # care of whether it is a zoom in or zoom out.
        elif self.mouseAction.tooltype == ToolType.ZoomTool:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        # Shape tool handler
        elif self.mouseAction.isShapeTool:

            # Draw if this is the left button
            if event.button() == QtCore.Qt.LeftButton:

                # Don't start drawing unless the pixmap is under the
                # mouse in the scene
                if not self.mainImage().isUnderMouse():
                    super().mousePressEvent(event)
                    return
                else:
                    pos = self.mapToScene(event.pos())
                    initialRect = QtCore.QRectF(pos.x(), pos.y(), 1, 1)
                    
                if self.mouseAction.tooltype == ToolType.OvalShape:
                    self._dynamicallyDrawnItem = sg.SceneCountDataEllipse.create(initialRect, self._pen)
                elif self.mouseAction.tooltype == ToolType.RectangleShape:
                    self._dynamicallyDrawnItem = sg.SceneCountDataRect.create(initialRect, self._pen)
                elif self.mouseAction.tooltype == ToolType.LineShape:
                    line = QtCore.QLineF(
                        pos.x(), pos.y(),
                        pos.x()+1, pos.y()+1)
                    self._dynamicallyDrawnItem = sg.SceneCountDataLine.create(line, self._pen)
                else:
                    self._dynamicallyDrawnItem = None

                if self._dynamicallyDrawnItem is not None:
                    self.scene().addItem(self._dynamicallyDrawnItem)

            # Erase if this is the right button
            elif event.button() == QtCore.Qt.RightButton:
                self._erasing = True
                self._removeDrawnItemsUnderPoint(self.mapToScene(event.pos()))
                self.setCursor(Cursors.eraser)

        elif self.mouseAction.tooltype == ToolType.Eraser:
            # When the mouse moves, if the mouse was pressed with this tool,
            # we need to know that we are still erasing
            self._erasing = True
            self._removeDrawnItemsUnderPoint(self.mapToScene(event.pos()))
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        # Update dynamically drawn object if it exists
        if self._dynamicallyDrawnItem is not None:

            # Prepare geometry for changing (since we're dragging it)
            self._dynamicallyDrawnItem.prepareGeometryChange()

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
        
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        super().mouseReleaseEvent(event)

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

                # Shapes with very small bounding rects should not be saved
                # Also, if this is valid, we want to show the count editor box
                if width > minLength and height > minLength:
                    valid = True

                    self._countForm.popup(self._dynamicallyDrawnItem, event.pos())

            # Some shapes use lines
            elif self.mouseAction.tooltype == ToolType.LineShape:

                # Very small lines should not be saved
                if self._dynamicallyDrawnItem.line().length() > minLength:
                    valid = True

            # Only save if the shape is a valid size
            if valid:
                self._emitDrawnItems()
            else:
                self.scene().removeItem(self._dynamicallyDrawnItem)

            # Reset object handle
            self._dynamicallyDrawnItem = None

            # We just used the mouse action -- let the controller know so it can go 
            # go back to the default action

        # If we just erased something, let the world know
        elif self._erasing:
            self._erasing = False
            self._updateCursor()
            self._emitDrawnItems()

        # If we were doing a rubberband drag,
        # figure out how to handle it.
        elif self.dragMode() == QtWidgets.QGraphicsView.RubberBandDrag:

            # This is the bounding box selected by the mouse
            selectionBBox = self.scene().selectionArea().boundingRect()

            # We might be zooming because the zoom tool is active.
            # If this is the case, we zoom *in* to the selection box
            # if the left mouse button is used, but zoom *out* from
            # the selection box if the right mouse button is used.
            if self.mouseAction.tooltype == ToolType.ZoomTool:
                if event.button() == QtCore.Qt.LeftButton:

                    # Zoom to the selected rectangle
                    self.zoomTo(selectionBBox)

                elif event.button() == QtCore.Qt.RightButton:

                    # Zoom out from the selected rectangle
                    self.zoomOutOneLevel()

            # Regardless of the reason we were in rubberband
            # drag mode, we don't want to be in that mode anymore
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

        elif self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:

            # Regardless of the reason we were in scroll hand
            # drag mode, we don't want to be in that mode anymore
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        
        # Let the controller know that we used a mouse action
        self.controller.mouseActionUsed()

    def mouseDoubleClickEvent(self, event):
        '''
        For the standard, hand tool:
        * Zoom in with the left button,
        * Zoom out with the right button
        '''
        if self.mouseAction.tooltype in (ToolType.HandTool, ToolType.ZoomTool):
            if event.button() == QtCore.Qt.LeftButton:
                self.zoomIn(0.10)
                
            elif event.button() == QtCore.Qt.RightButton:
                self.clearZoom()

        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        numPixels: QtCore.QPoint = event.pixelDelta()
        numDegrees: QtCore.QPoint = event.angleDelta() / 8

        if not numPixels.isNull():
            self.zoomWithPixels(numPixels)
        elif not numDegrees.isNull():
            numSteps: QtCore.QPoint = numDegrees / 15
            self.zoomWithDegrees(numSteps)

        event.accept()

    def zoomWithPixels(self, numPixels: QtCore.QPoint):
        self.zoomWithDegrees(numPixels)

    def zoomWithDegrees(self, numDegrees: QtCore.QPoint):
        zoomPercentage = numDegrees.y() / self.height()

        if zoomPercentage < 0:
            self.zoomOut(0.1)
        else:
            self.zoomIn(0.1)
