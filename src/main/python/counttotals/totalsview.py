
from PySide2 import QtCore, QtWidgets, QtGui

from .totalsmodel import TotalsModel
from .enums import UserRoles

class TotalsView(QtWidgets.QListView):
    
    fileActivated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setModel(TotalsModel())
        self.activated.connect(self.indexActivated)

        # Alternate row colors
        p = self.palette()
        p.setColor(p.AlternateBase, QtGui.QColor('#ffe8c9'))
        self.setPalette(p)
        self.setAlternatingRowColors(True)

    @QtCore.Slot(QtCore.QModelIndex)
    def indexActivated(self, index:QtCore.QModelIndex) -> str:
        if self.model().inTransect:
            fp = index.data(UserRoles.AbsolutePath)
            self.fileActivated.emit(fp)
