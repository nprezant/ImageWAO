from pathlib import Path

from PySide2 import QtCore, QtWidgets

from base import config

from .totalsmodel import TotalsModel
from .enums import UserRoles


class TotalsView(QtWidgets.QListView):

    fileActivated = QtCore.Signal(str)
    selectedFilesChanged = QtCore.Signal(Path)

    def __init__(self):
        super().__init__()
        self.setModel(TotalsModel())
        self.activated.connect(self.indexActivated)

        # Alternate row colors
        color = config.colors["green"]
        altColor = config.colors["lightgreen"]
        self.setAlternatingRowColors(True)
        self.setStyleSheet(
            f"background-color: {color}; alternate-background-color: {altColor};"
        )

        # Handle selection changes and map to appropriate signals
        self.selectionModel().selectionChanged.connect(self._handleSelectionChange)

        # Selection is sometimes changed programatically and this can lead to
        # infinite recursion. To combat this, we can tell the selectionChanged signal
        # to not be emitted when the selection is programatically changed.
        self.emitNextSelectionSignal = True

    @QtCore.Slot(QtCore.QModelIndex)
    def indexActivated(self, index: QtCore.QModelIndex) -> str:
        if self.model().inTransect:
            fp = index.data(UserRoles.AbsolutePath)
            self.fileActivated.emit(fp)

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _handleSelectionChange(self, selected, deselected):

        # If the selection was just changed programatically,
        # do not emit any further selection changed signals.
        if not self.emitNextSelectionSignal:
            self.emitNextSelectionSignal = True
            return

        # Retreive the selected indexes
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the files that are currently selected
        files = [Path(idx.data(role=UserRoles.AbsolutePath)) for idx in indexes]
        self.selectedFilesChanged.emit(files)

    @QtCore.Slot()
    def export(self):
        self.model().export()

    def selectFile(self, fp: str):
        """
        Selects the file or folder at the given path if possible.
        This has a bit of a recursion issue when you connect this to
        the library and the library back to this.
        """

        # Clear the current selection
        self.selectionModel().clearSelection()

        # Get name of item
        name = Path(fp).name

        # Get model indexes
        index = self.model().indexOfName(name)
        if index is None:
            return

        # Select new index
        self.emitNextSelectionSignal = False
        self.selectionModel().select(index, QtCore.QItemSelectionModel.Select)

        # Scroll to the index
        self.scrollTo(index)
