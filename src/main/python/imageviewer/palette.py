
from PySide2 import QtCore, QtGui, QtWidgets

class QPaletteIcon(QtGui.QIcon):

    def __init__(self, color):
        super().__init__()

        self.color = color

        pixmap = QtGui.QPixmap(100, 100)
        pixmap.fill(QtGui.QColor(color))
        self.addPixmap(pixmap)

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
