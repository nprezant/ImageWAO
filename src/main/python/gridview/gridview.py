
from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import QImageGridModel

class QImageGridView(QtWidgets.QTableView):

    # Convenience signal    
    selectedIndexesChanged = QtCore.Signal(list)

    def __init__(self):
        super().__init__()
        self.setModel(QImageGridModel())

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.selectionModel().selectionChanged.connect(self._emitSelectionChanged)

    def _emitSelectionChanged(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()
        self.selectedIndexesChanged.emit(indexes)


if __name__ == '__main__':
    pass
