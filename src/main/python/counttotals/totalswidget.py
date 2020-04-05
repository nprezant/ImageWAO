
from PySide2 import QtCore, QtWidgets, QtGui

from base import ctx, config
from .totalsview import TotalsView

class CountTotals(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()

        # Export Action
        self.exportAction = QtWidgets.QAction(ctx.icon('icons/excel.png'), 'Export', self)
        exportButton = QtWidgets.QToolButton()
        exportButton.setIconSize(QtCore.QSize(*config.toolbuttonSize))
        exportButton.setDefaultAction(self.exportAction)

        # Refresh Action
        self.refreshAction = QtWidgets.QAction(ctx.icon('icons/refresh.png'), 'Refresh', self)
        refreshButton = QtWidgets.QToolButton()
        refreshButton.setIconSize(QtCore.QSize(*config.toolbuttonSize))
        refreshButton.setDefaultAction(self.refreshAction)

        # Horizontal row of buttons at top
        buttons = QtWidgets.QHBoxLayout()
        buttons.setContentsMargins(5,0,0,0)
        buttons.addWidget(exportButton, alignment=QtCore.Qt.AlignLeft)
        buttons.addWidget(refreshButton, alignment=QtCore.Qt.AlignLeft)
        buttons.addStretch()

        # Totals view
        self.totalsView = TotalsView()

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addLayout(buttons)
        layout.addWidget(self.totalsView)
