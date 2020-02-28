
from PySide2 import QtCore, QtGui, QtWidgets

class ColorMenu(QtWidgets.QMenu):

    # When the color is changed, the new color will be emitted
    # from this signal
    colorChanged = QtCore.Signal(QtGui.QColor)

    def __init__(self, colors):
        '''
        Create and assign menu actions with icons corresponding
        to the input list of colors
        '''
        super().__init__()
        self.actions = []
        self._activeIndex = 0
        for color in colors:

            qcolor = QtGui.QColor(color)
            icon = self.circularColorIcon(qcolor)

            action = QtWidgets.QAction(icon, qcolor.name(QtGui.QColor.HexRgb))
            action.qcolor = qcolor
            action.setCheckable(True)
            action.triggered.connect(self.handleColorChanged)
            self.actions.append(action)
            self.addAction(action)

        # Initialize the first item as the one selected
        self._activeIndex = 0
        self.actions[0].setChecked(True)

    @property
    def activeColor(self):
        return self.actions[self._activeIndex].qcolor

    def emitActiveColor(self):
        '''
        Trigger an emit for the active index.
        This method is used internally, but can also be called externally
        to manually emit the colorChanged signal on the active index.
        This can be helpful when initializing the class after setting up
        the proper slots.
        '''
        self.colorChanged.emit(self.activeColor)

    @staticmethod
    def circularColorIcon(qcolor, w=100, h=100):
        '''
        Creates a circular icon with transparent background
        and solid color of a given width w and height h
        '''
        img = QtGui.QImage(w, h, QtGui.QImage.Format_ARGB32)
        img.fill(QtGui.qRgba(0, 0, 0, 0))
        painter = QtGui.QPainter(img)
        painter.setBrush(qcolor)
        painter.drawEllipse(5,5,w-10,h-10)
        painter.end()
        icon = QtGui.QIcon(QtGui.QPixmap.fromImage(img))
        return icon

    @staticmethod
    def maskedIcon(qcolor, maskImg:QtGui.QPixmap):
        '''
        Creates an icon of a given color from the given mask
        '''
        img = QtGui.QPixmap(maskImg.size())
        mask = maskImg.createMaskFromColor(QtGui.QColor('black'), QtCore.Qt.MaskOutColor)
        img.fill(qcolor)
        img.setMask(mask)
        return img

    def handleColorChanged(self, checked):

        # If we tried to uncheck an item, don't allow it
        if checked is False:
            self.actions[self._activeIndex].setChecked(True)
            return

        # Uncheck the previously active index
        self.actions[self._activeIndex].setChecked(False)

        # Find the new active action, change the active index,
        # and emit the color
        for i,a in enumerate(self.actions):
            if a.isChecked():
                self._activeIndex = i
                self.emitActiveColor()
                return


class ColorableAction(QtWidgets.QAction):
    '''
    An action whose icon can be re-colored with a mask.
    Instance also contains information about what kind of drawing
    it might perform
    '''
    def __init__(self, parent, mask: QtGui.QPixmap):
        super().__init__(parent)
        self.mask = mask
        self.setIcon(mask)

    def recolor(self, color: QtGui.QColor):
        self.setIcon(ColorMenu.maskedIcon(color, self.mask))
