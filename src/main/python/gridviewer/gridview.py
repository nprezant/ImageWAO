
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import QImageGridModel, UserRoles

class QImageGridView(QtWidgets.QTableView):

    selectedFilesChanged = QtCore.Signal(Path) # this prevents redundant signal emits
    selectedImageChanged = QtCore.Signal(QtGui.QImage) # this will let the grid determine what the viewer shows
    notificationMessage = QtCore.Signal(str) # notifications to the main application
    loadProgress = QtCore.Signal(int) # loading progress notification
    drawnItemsChanged = QtCore.Signal(str) # serialized string of items drawn on image

    def __init__(self):
        super().__init__()
        self.setModel(QImageGridModel())

        # Hide headers
        self.horizontalHeader().hide()
        self.verticalHeader().hide()

        # Resize headers to fit the contents
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        # Create context menu
        self.menu = QtWidgets.QMenu(self)
        self._populateContextMenu()

        # Context menu policy must be CustomContextMenu for us to implement
        # our own context menu. Connect the context menu request to our internal slot.
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)

        # Handle selection changes and map to appropriate signals
        self.selectionModel().selectionChanged.connect(self._handleSelectionChange)

        # Bubble progress updates from the model
        # (The model often has to perform expensive loading operations)
        self.model().progress.connect(self.loadProgress.emit)

    def _populateContextMenu(self):
        # Create context menu
        self.menu = QtWidgets.QMenu(self)

        # Create menu actions
        previewAction = QtWidgets.QAction('Preview', self)

        # Connect handlers for actions
        previewAction.triggered.connect(self._handlePreviewRequest)

        # Add actions to the menu
        self.menu.addAction(previewAction)

    @QtCore.Slot(QtCore.QPoint)
    def _customMenuRequested(self, pos:QtCore.QPoint):
        '''
        Open the context menu
        '''
        self.menu.popup(self.viewport().mapToGlobal(pos))

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _handleSelectionChange(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the first of the selected indexes
        index = indexes[0]
        if index.isValid():

            # Emit image
            self.selectedImageChanged.emit(index.data(role=UserRoles.FullResImage))

            # Only emit items if we find some
            items = index.data(role=UserRoles.DrawnItems)
            if items is not None:
                self.drawnItemsChanged.emit(items)

        # Emit the files that are currently selected
        files = [idx.data(role=UserRoles.ImagePath) for idx in indexes]
        self.selectedFilesChanged.emit(files)

    @QtCore.Slot()
    def _handlePreviewRequest(self):
        '''
        Requests a preview of all selected images
        from the model, emitting that in the selectedImageChanged
        signal
        '''
        indexes = self.selectionModel().selectedIndexes()
        preview = self.model().mergeIndexes(indexes)
        if preview is not None:
            self.selectedImageChanged.emit(preview)


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
            self.notificationMessage.emit(
                'Images still loading...\n\n'
                f'No image parts were found at the requested path:\n{path}')
        else:

            # Ensure the index associated with this file is visible
            self.scrollTo(idx)

            # Select the entire image associated with the first index
            self.selectedImageChanged.emit(idx.data(role=UserRoles.EntireImage))

    @QtCore.Slot(str)
    def saveDrawnItems(self, items):
        '''
        Save the drawn items passed in to the currently active
        model index.
        '''
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Save the drawn items to the first of the selected indexes
        # TODO: Handle if multiple indexes are selected
        index = indexes[0]

        self.model().setDrawnItems(index, items)


if __name__ == '__main__':
    pass
