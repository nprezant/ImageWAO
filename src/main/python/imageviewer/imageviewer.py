# from PySide2.QtCore import Qt, QRectF, QMarginsF, QTimeLine, Signal, QSize
# from PySide2.QtGui import QKeySequence, QImage, QPixmap, QPalette, QPainter, QWheelEvent, QtGui.QKeyEvent, QIcon, QPen, QColor
# from PySide2.QtWidgets import (
#     QGraphicsView, QGraphicsScene, QGraphicsItem, QToolBar, QtWidgets.QAction,
#     QApplication, QInputDialog, QMenu, QToolButton, QPushButton
# )

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

    def __init__(self):
        super().__init__()

        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)

        self.mainPixmapItem = self.scene.addPixmap(QtGui.QPixmap())

        self._appContext = None

        # policies
        # self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
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

        # self.updateDragMode()

    @property
    def appContext(self):
        return self._appContext

    @appContext.setter
    def appContext(self, context):
        self._appContext = context
        self.toolbar.clear()
        self.initToolbar()

    def setMainPixmapFromPath(self, imgPath):

        # set image
        image = QtGui.QImage(str(imgPath))
        pixmap = self.mainPixmapItem.pixmap()
        pixmap.convertFromImage(image)
        self.setMainPixmap(pixmap)

    def setMainPixmap(self, pixmap):
        self.mainPixmapItem.setPixmap(pixmap)

        # set scene rect
        boundingRect = self.mainPixmapItem.boundingRect()
        margin = 0
        boundingRect += QtCore.QMarginsF(margin,margin,margin,margin)
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

    def scaleView(self, scaleFactor):
        # print(f'self.width: {self.width()}')
        # print(f'pixmap.width(): {self.scene.map.mainPixmapItem.boundingRect().width()}')
        self.scale(scaleFactor, scaleFactor)

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

    def setResourcePaths(self):
        if self.appContext is None:
            self.selectionModeFp = '../resources/base/home.png'
            self.ovalModeFp = '../resources/base/home.png'
            self.flattenFp = '../resources/base/home.png'
            self.undoFp = '../resources/base/home.png'
            self.penFp = '../resources/base/home.png'
            self.penWidthFp = '../resources/base/home.png'
        else:
            self.selectionModeFp = self.appContext.get_resource('selectIcon.png')
            self.ovalModeFp = self.appContext.get_resource('ovalIcon.png')
            self.flattenFp = self.appContext.get_resource('saveIcon.png')
            self.undoFp = self.appContext.get_resource('undoIcon.png')
            self.penFp = self.appContext.get_resource('pen.png')
            self.penWidthFp = self.appContext.get_resource('penWidth.png')

    def createActions(self):
        self.setResourcePaths()
        
        # self.selectionModeAct = QtWidgets.QAction('Select (v)', self, checkable=True, checked=True, shortcut=QtCore.Qt.Key_V, triggered=self.toggleSelectionMode)
        # self.ovalModeAct = QtWidgets.QAction('Draw &Oval (o)', self, checkable=True, checked=False, shortcut=QtCore.Qt.Key_O, triggered=self.toggleOvalMode)
        # self.flattenAct = QtWidgets.QAction('Save', self, shortcut=QtGui.QKeySequence.Save, triggered=self.flattenImage)
        # self.undoAct = QtWidgets.QAction('Undo', self, shortcut=QtGui.QKeySequence.Undo, triggered=self.removeLastDrawnItem)
        # self.selectionModeAct = QtWidgets.QAction(QtGui.QIcon(self.selectionModeFp), 'Select (v)', self, checkable=True, checked=True, shortcut=QtCore.Qt.Key_V, triggered=self.toggleSelectionMode)
        # self.ovalModeAct = QtWidgets.QAction(QtGui.QIcon(self.ovalModeFp), 'Draw &Oval (o)', self, checkable=True, checked=False, shortcut=QtCore.Qt.Key_O, triggered=self.toggleOvalMode)
        # self.flattenAct = QtWidgets.QAction(QtGui.QIcon(self.flattenFp), 'Save', self, shortcut=QtGui.QKeySequence.Save, triggered=self.flattenImage)
        # self.undoAct = QtWidgets.QAction(QtGui.QIcon(self.undoFp), 'Undo', self, shortcut=QtGui.QKeySequence.Undo, triggered=self.removeLastDrawnItem)

        self.setPenWidthAct = QtWidgets.QAction('Set Pen Width', self, triggered=self.promptForPenWidth)

    def addPenToolMenu(self):
        penButton = QtWidgets.QToolButton(self)
        penButton.setText('Pen')
        penButton.setIcon(QtGui.QIcon(self.penFp))
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
        # self.toolbar.addAction(self.flattenAct)
        # self.toolbar.addAction(self.undoAct)
        # # self.toolbar.addSeparator()
        # self.toolbar.addAction(self.selectionModeAct)
        # self.toolbar.addAction(self.ovalModeAct)
        self.addPenToolMenu()


class QImagePainterToolbar(QtWidgets.QToolBar):

    def __init__(self):
        super().__init__()
