
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

    def reset(self):
        '''
        Initialize the first value as checked and trigger.
        This method should be called AFTER the slots are set up
        for the colorChanged signal.
        '''
        self._activeIndex = 0
        self.actions[0].setChecked(True)
        self.colorChanged.emit(self.actions[0].qcolor)

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
                self.colorChanged.emit(a.qcolor)
                return
