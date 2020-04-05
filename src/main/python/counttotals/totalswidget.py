
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from base import ctx, config
from .totalsview import TotalsView

class CountTotals(QtWidgets.QWidget):

    fileActivated = QtCore.Signal(str)
    selectedFilesChanged = QtCore.Signal(Path)
    
    def __init__(self):
        super().__init__()

        # Totals view
        self.totalsView = TotalsView()
        self.totalsView.fileActivated.connect(self.fileActivated.emit)
        self.totalsView.selectedFilesChanged.connect(self.selectedFilesChanged.emit)

        # Export Action
        self.exportAction = QtWidgets.QAction(ctx.icon('icons/excel.png'), 'Export', self)
        self.exportAction.triggered.connect(self.totalsView.export)
        exportButton = QtWidgets.QToolButton()
        exportButton.setIconSize(QtCore.QSize(*config.toolbuttonSize))
        exportButton.setDefaultAction(self.exportAction)
        exportButton.setToolTip('Copies data to clipboard. Paste data into Excel (or any text editor)')

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

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addLayout(buttons)
        layout.addWidget(self.totalsView)
    
    @QtCore.Slot(str)
    @QtCore.Slot(Path)
    def readDirectory(self, fp):
        '''
        Reads the directory.
        `fp` is any Path() - able type.
        '''
        self.totalsView.model().readDirectory(fp)
