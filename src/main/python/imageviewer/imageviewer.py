
from PySide2 import QtCore, QtGui, QtWidgets


class QImageViewer(QtWidgets.QGraphicsView):

    def __init__(self):
        super().__init__()

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.setScene(QtWidgets.QGraphicsScene())

        # Image aspect ratio mode.
        # !!! ONLY applies to full image. Aspect ratio is always ignored when zooming.
        #   Qt.IgnoreAspectRatio: Scale image to fit viewport.
        #   Qt.KeepAspectRatio: Scale image to fit inside viewport, preserving aspect ratio.
        #   Qt.KeepAspectRatioByExpanding: Scale image to fill the viewport, preserving aspect ratio.
        self.aspectRatioMode = QtCore.Qt.KeepAspectRatio

        # Scroll bar behaviour.
        #   Qt.ScrollBarAlwaysOff: Never shows a scroll bar.
        #   Qt.ScrollBarAlwaysOn: Always shows a scroll bar.
        #   Qt.ScrollBarAsNeeded: Shows a scroll bar only when zoomed.
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        # Stack of QRectF zoom boxes in scene coordinates.
        self.zoomStack = []

        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

    def viewBoundingBox(self):
        '''
        Bounding box of the current view.
        '''
        A = self.mapToScene(QtCore.QPoint(0, 0)) 
        B = self.mapToScene(QtCore.QPoint(
            self.viewport().width(), 
            self.viewport().height()))
        viewBBox = QtCore.QRectF(A, B)

        # This box might include parts of the scene outside
        # the rect -- this is invalid. Need to intersect with
        # the scene rect.
        return viewBBox.intersected(self.sceneRect())

    @QtCore.Slot(QtGui.QImage)
    def setImage(self, image:QtGui.QImage):
        '''
        Set the scene's current image pixmap to the input QImage
        '''
        pixmap = QtGui.QPixmap.fromImage(image)

        # Add the pixmap to the scene and set a custom attribute so we
        # can find it with scene().items()
        item = self.scene().addPixmap(pixmap)
        item._mainViewerItem = True

        # set scene size to image size.
        self.setSceneRect(QtCore.QRectF(pixmap.rect()))

        if self.canZoom:
            self.zoomStack = []  # Clear zoom stack.

        self.updateViewer()

    def hasMainImage(self):
        '''
        Checks to see if the image set with `setImage` is
        in the scene.
        '''
        mainImage = self.mainImage()
        if mainImage is None:
            return False
        else:
            return True

    def mainImage(self):
        '''
        Returns main pixmap item, or `None` if it cannot be found.
        '''
        for item in self.scene().items():
            try:
                _ = item._mainViewerItem
            except AttributeError:
                continue
            else:
                return item
        return None

    def updateViewer(self):
        '''
        Show current zoom (if showing entire image, apply current aspect ratio mode).
        '''
        if not self.hasMainImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.KeepAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        '''
        Maintain current zoom on resize.
        '''
        self.updateViewer()

    def clearZoom(self):
        '''
        Clears and resets the zoom stack
        '''
        self.zoomStack = []
        self.updateViewer()

    def zoomIn(self, percent):
        '''
        Zooms the view in by a given percent.
        Percentage on scale of 0 to 1.
        '''
        viewBBox = self.viewBoundingBox()
        margin = int(viewBBox.width() * percent)
        smallerRect = viewBBox.marginsRemoved(QtCore.QMargins(margin, margin, margin, margin))
        self.zoomTo(smallerRect)

    def zoomOut(self, percent):
        '''
        Zooms the view out by a given percent
        Percentage on scale of 0 to 1
        '''
        viewBBox = self.viewBoundingBox()
        margin = int(viewBBox.width() * percent)
        largerRect = viewBBox.marginsAdded(QtCore.QMargins(margin, margin, margin, margin))
        self.zoomTo(largerRect)

    def zoomTo(self, rect):
        '''
        Zoom the view to the given rectangle.
        This is most commonly used with rubberband
        selection rectangles
        '''
        
        viewBBox = self.sceneRect()
        
        # The box that we want to zoom to is the one that
        # intersects with the view's bounding box.
        # (E.g. if the requested box is outside the scene,
        # clip the box to the scene's limits)
        selectionBBox = rect.intersected(viewBBox)

        # Clear current selection area.
        self.scene().setSelectionArea(QtGui.QPainterPath())

        # Execute zoom
        if selectionBBox.isValid() and (selectionBBox != viewBBox):
            self.zoomStack.append(selectionBBox)
            self.updateViewer()

    def zoomOutOneLevel(self):
        '''
        Zooms the view by a single zoom level.
        '''
        if len(self.zoomStack):
            self.zoomStack.pop()
            self.updateViewer()

