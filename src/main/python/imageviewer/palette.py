
from PySide2 import QtCore, QtGui, QtWidgets

class QPaletteIcon(QtGui.QIcon):

    def __init__(self, color):
        super().__init__()

        self.color = color

        img = QtGui.QImage(100, 100, QtGui.QImage.Format_ARGB32_Premultiplied)
        painter = QtGui.QPainter(img)
        painter.setBrush(QtGui.QColor(color))
        painter.drawEllipse(5,5,90,90)
        painter.end()
        self.addPixmap(QtGui.QPixmap.fromImage(img))

    @staticmethod
    def createColorActions(colors):
        ''' Create and return a list of actions with
        QPaletteIcons corresponding to the input list of colors
        '''
        actions = []
        for color in colors:
            paletteIcon = QPaletteIcon(color)
            action = QtWidgets.QAction(paletteIcon, 'Color')
            action.setCheckable(True)
            action.color = color
            action.triggered.connect(lambda : print(f'Color changed'))
            actions.append(action)
        return actions
