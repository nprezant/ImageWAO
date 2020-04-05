
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

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
        p = self.palette()
        p.setColor(p.AlternateBase, QtGui.QColor('#ffe8c9'))
        self.setPalette(p)
        self.setAlternatingRowColors(True)

        # Handle selection changes and map to appropriate signals
        self.selectionModel().selectionChanged.connect(self._handleSelectionChange)

    @QtCore.Slot(QtCore.QModelIndex)
    def indexActivated(self, index:QtCore.QModelIndex) -> str:
        if self.model().inTransect:
            fp = index.data(UserRoles.AbsolutePath)
            self.fileActivated.emit(fp)

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _handleSelectionChange(self, selected, deselected):
        model = self.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the files that are currently selected
        files = [Path(idx.data(role=UserRoles.AbsolutePath)) for idx in indexes]
        self.selectedFilesChanged.emit(files)

