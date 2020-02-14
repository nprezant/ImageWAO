
from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from .smoothing import QSmoothGraphicsView


COLORS = {
    'Teleric Blue': '#3296e6',
    'Blue': 'Blue',
    'Green': 'DarkGreen',
    'Teal': 'Teal',
    'Red': 'Red',
    'Orange': 'Orange',
    'Magenta': 'Magenta',
    'Black': 'Black',
    'White': 'White',
}

class QPaletteIcon(QtGui.QIcon):

    def __init__(self, color):
        super().__init__()

        self.color = color

        pixmap = QtGui.QPixmap(100, 100)
        pixmap.fill(QtGui.QColor(color))
        self.addPixmap(pixmap)

class QImageViewer(QSmoothGraphicsView):

    # signals
    imageFlattened = QtCore.Signal(QtGui.QImage)

    def __init__(self, ctx):
        super().__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)

        self.mainPixmapItem = self.scene.addPixmap(QtGui.QPixmap())

        self.ctx = ctx

        # policies
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.toolbar = QtWidgets.QToolBar()
        self.initToolbar()

        self._pen = QtGui.QPen()
        self._pen.setWidth(50)
        self.setDefaultPenColor()

        self._drawStartPos = None
        self._dynamicOval = None
        self._drawnItems = []

        self.updateDragMode()

    def trySetFromPath(self, path):
        p = Path(path)
        if p.suffix.lower() in ('.jpg', '.png'):
            self.setMainPixmapFromPath(path)
        else:
            print('image not valid')

    def setMainPixmapFromPath(self, imgPath):

        # set image
        pixmap = QtGui.QPixmap(imgPath)
        self.setMainPixmap(pixmap)

    def setMainPixmap(self, pixmap):
        self.mainPixmapItem.setPixmap(pixmap)

        # set scene rect
        boundingRect = self.mainPixmapItem.boundingRect()
        w = boundingRect.width()
        h = boundingRect.height()
        marginFactor = 0.5
        boundingRect += QtCore.QMarginsF(
            w * marginFactor, h * marginFactor,
            w * marginFactor, h * marginFactor)
        self.scene.setSceneRect(boundingRect)

    def saveImage(self, fileName):
        image = self.flattenImage()
        image.save(fileName)

    def flattenImageIfDrawnOn(self):
        if not len(self._drawnItems) == 0:
            self.flattenImage()

    def flattenImage(self):

        # get region of scene
        area = self.mainPixmapItem.boundingRect()

        # create a QImage to render to and fix up a QPainter for it
        image = QtGui.QImage(area.width(), area.height(), QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(image)

        # render the region of interest to the QImage
        self.scene.render(painter, QtCore.QRectF(image.rect()), area)
        painter.end()

        # set this flattened image to this view
        pixmap = self.mainPixmapItem.pixmap()
        pixmap.convertFromImage(image)
        self.setMainPixmap(pixmap)

        # clear the drawings from the view
        self.clearDrawnItems()

        # emit flattened image signal
        self.imageFlattened.emit(image)

        # return the flattened image
        return image

    def clearDrawnItems(self):
        for item in self._drawnItems:
            self.scene.removeItem(item)

        self._drawnItems.clear()

    def removeLastDrawnItem(self):
        try:
            item = self._drawnItems.pop()
        except IndexError:
            pass
        else:
            self.scene.removeItem(item)

    def centerImage(self):
        self.centerOn(self.mainPixmapItem)

    def bestFitImage(self):
        self.fitInView(self.mainPixmapItem, QtCore.Qt.KeepAspectRatio)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        key = event.key()
        if key == QtCore.Qt.Key_Space:
            self.bestFitImage()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        self._drawStartPos = None
        if self.ovalModeAct.isChecked():
            if self.mainPixmapItem.isUnderMouse():
                self._drawStartPos = self.mapToScene(event.pos())
                self._dynamicOval = self.scene.addEllipse(
                    QtCore.QRectF(self._drawStartPos.x(), self._drawStartPos.y(), 1, 1),
                    self._pen
                )
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dynamicOval:
            pos = self.mapToScene(event.pos())
            self._dynamicOval.setRect(
                QtCore.QRectF(self._drawStartPos.x(), self._drawStartPos.y(),
                pos.x() - self._drawStartPos.x(), pos.y() - self._drawStartPos.y())
            )
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dynamicOval:
            self._drawnItems.append(self._dynamicOval)
            self._dynamicOval = None
        else:
            super().mouseReleaseEvent(event)

    def toggleSelectionMode(self):
        if self.selectionModeAct.isChecked():
            self.ovalModeAct.setChecked(False)
        else:
            self.selectionModeAct.setChecked(True)
        self.updateDragMode()

    def toggleOvalMode(self):
        if self.ovalModeAct.isChecked():
            self.selectionModeAct.setChecked(False)
        else:
            self.ovalModeAct.setChecked(True)
        self.updateDragMode()

    def updateDragMode(self):
        if self.selectionModeAct.isChecked():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    @property
    def penWidth(self):
        return self._pen.width()

    @penWidth.setter
    def penWidth(self, value):
        self._pen.setWidth(value)

    @property
    def penColor(self):
        return self._pen.color()

    @penColor.setter
    def penColor(self, value):
        self._pen.setColor(QtGui.QColor(value))

    def setDefaultPenColor(self):
        self.setPenColor(COLORS['Teleric Blue']) 

    def promptForPenWidth(self):
        width, okPressed = QtWidgets.QInputDialog.getInt(self, 'Pen Width','Pen width (px):', self.penWidth, 1, 100, 1)
        if okPressed:
            self.penWidth = width        

    def createActions(self):
        selectionModeFp = self.ctx.get_resource('selectIcon.png')
        ovalModeFp = self.ctx.get_resource('ovalIcon.png')
        flattenFp = self.ctx.get_resource('saveIcon.png')
        undoFp = self.ctx.get_resource('undoIcon.png')
        
        self.selectionModeAct = QtWidgets.QAction(QtGui.QIcon(selectionModeFp), 'Select (v)', self)
        self.selectionModeAct.setCheckable(True)
        self.selectionModeAct.setChecked(True)
        self.selectionModeAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_V))
        self.selectionModeAct.triggered.connect(self.toggleSelectionMode)

        self.ovalModeAct = QtWidgets.QAction(QtGui.QIcon(ovalModeFp), 'Draw &Oval (o)', self)
        self.ovalModeAct.setCheckable(True)
        self.ovalModeAct.setChecked(False)
        self.ovalModeAct.setShortcut(QtGui.QKeySequence(QtCore.Qt.Key_O))
        self.ovalModeAct.triggered.connect(self.toggleOvalMode)
        
        self.flattenAct = QtWidgets.QAction(QtGui.QIcon(flattenFp), 'Save', self)
        self.flattenAct.setShortcut(QtGui.QKeySequence.Save)
        self.flattenAct.triggered.connect(self.flattenImage)
        
        self.undoAct = QtWidgets.QAction(QtGui.QIcon(undoFp), 'Undo', self)
        self.undoAct.setShortcut(QtGui.QKeySequence.Undo)
        self.undoAct.triggered.connect(self.removeLastDrawnItem)

        self.setPenWidthAct = QtWidgets.QAction('Set Pen Width', self)
        self.setPenWidthAct.triggered.connect(self.promptForPenWidth)

    def addPenToolMenu(self):
        penFp = self.ctx.get_resource('pen.png')
        penWidthFp = self.ctx.get_resource('penWidth.png')

        penButton = QtWidgets.QToolButton(self)
        penButton.setText('Pen')
        penButton.setIcon(QtGui.QIcon(penFp))
        penButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.penMenu = QtWidgets.QMenu(penButton)
        self.penMenu.addAction(self.setPenWidthAct)

        self.addPaletteToMenu(self.penMenu)

        penButton.setMenu(self.penMenu)

        self.toolbar.addWidget(penButton)

    def setPenColor(self, color):
        qColor = QtGui.QColor(color)
        for a in self.penMenu.actions():
            a.setChecked(False)
            try:
                actionColor = QtGui.QColor(a.color)
            except AttributeError:
                pass
            else:
                if actionColor == qColor:
                    a.setChecked(True)
                    self.penColor = actionColor

    def addPaletteToMenu(self, menu):
        for name, color in COLORS.items():
            paletteIcon = QPaletteIcon(color)
            action = QtWidgets.QAction(paletteIcon, name, self, checkable=True)
            action.color = color
            action.triggered.connect(lambda checked, color=color: self.setPenColor(color))
            menu.addAction(action)

    def initToolbar(self):
        self.createActions()
        self.toolbar.addAction(self.flattenAct)
        self.toolbar.addAction(self.undoAct)
        # self.toolbar.addSeparator()
        self.toolbar.addAction(self.selectionModeAct)
        self.toolbar.addAction(self.ovalModeAct)
        self.addPenToolMenu()


class QImagePainterToolbar(QtWidgets.QToolBar):

    def __init__(self):
        super().__init__()
