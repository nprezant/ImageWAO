
from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import ImageGridModel

class QImageGridView(QtWidgets.QTableView):

     def __init__(self):
        super().__init__()
        self.setModel(ImageGridModel())

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)


if __name__ == '__main__':
    pass
