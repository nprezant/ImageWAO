''' QtImageViewer.py: PyQt image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
'''

import os.path

from PySide2 import QtCore, QtGui, QtWidgets


class QImageViewer(QtWidgets.QGraphicsView):
    ''' Image viewer widget for a QPixmap in a QGraphicsView scene with mouse zooming and panning.
    Displays a QImage or QPixmap (QImage is internally converted to a QPixmap).

    Mouse interaction:
        Left mouse button drag: Pan image.
        Right mouse button drag: Zoom box.
        Right mouse button doubleclick: Zoom to show entire image.
    '''

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = QtCore.Signal(float, float)
    rightMouseButtonPressed = QtCore.Signal(float, float)
    leftMouseButtonReleased = QtCore.Signal(float, float)
    rightMouseButtonReleased = QtCore.Signal(float, float)
    leftMouseButtonDoubleClicked = QtCore.Signal(float, float)
    rightMouseButtonDoubleClicked = QtCore.Signal(float, float)

    def __init__(self):
        super().__init__()

        # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        # Store a local handle to the scene's current image pixmap.
        self._pixmapHandle = None

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

    def hasImage(self):
        ''' Returns whether or not the scene contains an image pixmap.
        '''
        return self._pixmapHandle is not None

    def clearImage(self):
        ''' Removes the current image pixmap from the scene if it exists.
        '''
        if self.hasImage():
            self.scene.removeItem(self._pixmapHandle)
            self._pixmapHandle = None

    def pixmap(self):
        ''' Returns the scene's current image pixmap as a QPixmap, or else None if no image exists.
        :rtype: QPixmap | None
        '''
        if self.hasImage():
            return self._pixmapHandle.pixmap()
        return None

    def image(self):
        ''' Returns the scene's current image pixmap as a QImage, or else None if no image exists.
        :rtype: QImage | None
        '''
        if self.hasImage():
            return self._pixmapHandle.pixmap().toImage()
        return None

    def scenePixmap(self):
        return self._pixmapHandle

    def setImage(self, image):
        ''' Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        '''
        if type(image) is QtGui.QPixmap:
            pixmap = image
        elif type(image) is QtGui.QImage:
            pixmap = QtGui.QPixmap.fromImage(image)
        else:
            raise RuntimeError('ImageViewer.setImage: Argument must be a QImage or QPixmap.')
        if self.hasImage():
            self._pixmapHandle.setPixmap(pixmap)
        else:
            self._pixmapHandle = self.scene.addPixmap(pixmap)
        self.setSceneRect(QtCore.QRectF(pixmap.rect()))  # Set scene size to image size.
        if self.canZoom:
            self.zoomStack = []  # Clear zoom stack.
        self.updateViewer()

    def loadImageFromFile(self, fileName=''):
        ''' Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        '''
        if len(fileName) == 0:
            fileName, dummy = QtWidgets.QFileDialog.getOpenFileName(self, 'Open image file.')
        if len(fileName) and os.path.isfile(fileName):
            image = QtGui.QImage(fileName)
            self.setImage(image)

    def updateViewer(self):
        ''' Show current zoom (if showing entire image, apply current aspect ratio mode).
        '''
        if not self.hasImage():
            return
        if len(self.zoomStack) and self.sceneRect().contains(self.zoomStack[-1]):
            self.fitInView(self.zoomStack[-1], QtCore.Qt.KeepAspectRatio)  # Show zoomed rect (ignore aspect ratio).
        else:
            self.zoomStack = []  # Clear the zoom stack (in case we got here because of an invalid zoom).
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image (use current aspect ratio mode).

    def resizeEvent(self, event):
        ''' Maintain current zoom on resize.
        '''
        self.updateViewer()

    def mousePressEvent(self, event):
        ''' Start mouse pan or zoom mode.
        '''
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.rightMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        ''' Stop mouse pan or zoom mode (apply zoom if valid).
        '''
        super().mouseReleaseEvent(event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                selectionBBox = self.scene.selectionArea().boundingRect().intersected(viewBBox)
                self.scene.setSelectionArea(QtGui.QPainterPath())  # Clear current selection area.
                if selectionBBox.isValid() and (selectionBBox != viewBBox):
                    self.zoomStack.append(selectionBBox)
                    self.updateViewer()
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.rightMouseButtonReleased.emit(scenePos.x(), scenePos.y())

    def mouseDoubleClickEvent(self, event):
        ''' Show entire image.
        '''
        scenePos = self.mapToScene(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.canZoom:
                viewBBox = self.zoomStack[-1] if len(self.zoomStack) else self.sceneRect()
                margin = int(viewBBox.width() / 10)
                smallerRect = viewBBox.marginsRemoved(QtCore.QMargins(margin, margin, margin, margin))
                self.zoomStack.append(smallerRect)
                self.updateViewer()
        elif event.button() == QtCore.Qt.RightButton:
            if self.canZoom:
                self.zoomStack = []  # Clear zoom stack.
                self.updateViewer()
            self.rightMouseButtonDoubleClicked.emit(scenePos.x(), scenePos.y())
        super().mouseDoubleClickEvent(event)


if __name__ == '__main__':
    import sys

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print('Clicked on image pixel (row='+str(row)+', column='+str(column)+')')

    # Create the application.
    app = QtWidgets.QApplication(sys.argv)

    # Create image viewer and load an image file to display.
    viewer = QImageViewer()
    viewer.loadImageFromFile()  # Pops up file dialog.

    # Handle left mouse clicks with custom slot.
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # Show viewer and run application.
    viewer.show()
    sys.exit(app.exec_())