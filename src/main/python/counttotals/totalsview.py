
from PySide2 import QtCore, QtWidgets, QtGui

from .totalsmodel import TotalsModel

class TotalsView(QtWidgets.QListView):
    
    def __init__(self):
        super().__init__()
        self.setModel(TotalsModel())
