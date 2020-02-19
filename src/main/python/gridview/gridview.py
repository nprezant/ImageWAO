
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import QImageGridModel, UserRoles

class QImageGridView(QtWidgets.QTableView):

    selectedFilesChanged = QtCore.Signal(Path) # this prevents redundant signal emits
    selectedImageChanged = QtCore.Signal(QtGui.QImage) # this will let the grid determine what the viewer shows

    def __init__(self):
        super().__init__()
        self.setModel(QImageGridModel())

        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.selectionModel().selectionChanged.connect(self._handleSelectionChange)

    def _handleSelectionChange(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the first of the selected indexes
        index = indexes[0]
        if index.isValid():
            self.selectedImageChanged.emit(index.data(role=UserRoles.FullResImage))

        # Emit the files that are currently selected
        files = [idx.data(role=UserRoles.ImagePath) for idx in indexes]
        self.selectedFilesChanged.emit(files)

    def selectFile(self, path):
        ''' Selects all the items associated
        with a given file path
        '''
        self.selectionModel().clearSelection()
        indexes = self.model().matchPath(path)
        for idx in indexes:
            self.selectionModel().select(idx, QtCore.QItemSelectionModel.Select)

        try:
            idx = indexes[0]
        except IndexError:
            print(f'No indexes were found matching the requested path: {path}')
        else:

            # Ensure the index associated with this file is visible
            self.scrollTo(idx)

            # Select the entire image associated with the first index
            self.selectedImageChanged.emit(idx.data(role=UserRoles.EntireImage))


if __name__ == '__main__':
    pass
