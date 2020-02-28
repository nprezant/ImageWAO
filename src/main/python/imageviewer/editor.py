
from enum import Enum

from PySide2 import QtCore, QtGui, QtWidgets

from .imageviewer2 import QImageViewer
from .controls import ImageController, ColorableAction, ctx


class ToolType(Enum):
    Default = 0
    HandTool = 1
    ZoomTool = 2
    OvalShape = 3
    RectangleShape = 4
    LineShape = 5


class QImageEditor(QImageViewer):

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
        ]
        self.controller = ImageController(self, selectionActions)

        # Drawing pen
        self._pen = QtGui.QPen()
        self._pen.setWidth(30)

        # Connections
        self.controller.colorChanged.connect(self._updatePenColor)
        self.controller.sendSignals()

        # Drawing variables
        self._drawnItems = []
        self._dynamiclyDrawnObject = None
        
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

    @QtCore.Slot(QtGui.QColor)
    def _updatePenColor(self, qcolor):
        '''
        Set internal pen color, used for new drawings
        '''
        self._pen.setColor(qcolor)

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

            # Don't start drawing unless the pixmap is under the
            # mouse in the scene
            if not self.scenePixmap().isUnderMouse():
                super().mousePressEvent(event)
                return
            else:
                pos = self.mapToScene(event.pos())
                initialRect = QtCore.QRectF(pos.x(), pos.y(), 1, 1)
                
            if self.mouseAction.tooltype == ToolType.OvalShape:
                self._dynamiclyDrawnObject = self.scene.addEllipse(initialRect, self._pen)
            elif self.mouseAction.tooltype == ToolType.RectangleShape:
                self._dynamiclyDrawnObject = self.scene.addRect(initialRect, self._pen)
            elif self.mouseAction.tooltype == ToolType.LineShape:
                line = QtCore.QLineF(
                    pos.x(), pos.y(),
                    pos.x()+1, pos.y()+1)
                self._dynamiclyDrawnObject = self.scene.addLine(line, self._pen)

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        # Update dynamically drawn object if it exists
        if self._dynamiclyDrawnObject is not None:

            # Current mouse position
            pos = self.mapToScene(event.pos())

            # Some shapes use rectangles
            if self.mouseAction.tooltype in (ToolType.OvalShape, ToolType.RectangleShape):
                rect = self._dynamiclyDrawnObject.rect()
                rect.setBottomRight(QtCore.QPointF(pos.x(), pos.y()))
                self._dynamiclyDrawnObject.setRect(rect)

            # Some shapes use lines
            elif self.mouseAction.tooltype == ToolType.LineShape:
                line = self._dynamiclyDrawnObject.line()
                line.setP2(QtCore.QPointF(pos.x(), pos.y()))
                self._dynamiclyDrawnObject.setLine(line)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        # Save the most recent drawn object if it exists
        if self._dynamiclyDrawnObject is not None:

            # Only save is shape is a valid size
            valid = False
            minLength = self._pen.width()

            # Some shapes use rectangles
            if self.mouseAction.tooltype in (ToolType.OvalShape, ToolType.RectangleShape):
                rect = self._dynamiclyDrawnObject.rect()

                # Absolute value required because items have negative
                # width/height when they are drawn from right to left
                width = abs(rect.width())
                height = abs(rect.height())

                if width > minLength and height > minLength:
                    valid = True                

            # Some shapes use lines
            elif self.mouseAction.tooltype == ToolType.LineShape:

                if self._dynamiclyDrawnObject.line().length() > minLength:
                    valid = True

            # Only save if the shape is a valid size
            if valid:
                self._drawnItems.append(self._dynamiclyDrawnObject)
            else:
                self.scene.removeItem(self._dynamiclyDrawnObject)

            # Reset object handle
            self._dynamiclyDrawnObject = None

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
