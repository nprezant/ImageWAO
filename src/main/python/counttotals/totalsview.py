
from PySide2 import QtCore, QtWidgets, QtGui

from .totalsmodel import TotalsModel
from .enums import UserRoles

class TotalsView(QtWidgets.QListView):
    
    fileActivated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setModel(TotalsModel())
        self.activated.connect(self.indexActivated)

    @QtCore.Slot(QtCore.QModelIndex)
    def indexActivated(self, index:QtCore.QModelIndex) -> str:
        fp = index.data(UserRoles.AbsolutePath)
        self.fileActivated.emit(fp)
