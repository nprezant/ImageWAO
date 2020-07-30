
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from base import config
from tools import FileNameValidator

from .ids import PageIds

class SetLibraryPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Copy Images')
        self.setSubTitle('What do you want your folder of transects to be called?.')

        # import to this folder name
        self.flightFolderLabel = QtWidgets.QLabel('Name')
        self.flightFolderLabel.setMinimumWidth (
            self.flightFolderLabel.fontMetrics().boundingRect('Name ').width()
        )
        self.flightFolderBox = QtWidgets.QLineEdit('Flight XX')
        self.flightFolderBox.setValidator(FileNameValidator())
        self.registerField('flightFolder', self.flightFolderBox)
        
        # import to this path
        self.pathLabel = QtWidgets.QLabel('Create folder in:')
        self.pathLabel.setToolTip('By default this is your library folder.')
        self.pathEdit = QtWidgets.QLineEdit(config.libraryDirectory)
        self.pathEdit.setToolTip(self.pathLabel.toolTip())
        self.pathEdit.setReadOnly(True)
        self.pathEdit.setStyleSheet(
            'QLineEdit { '
            f'background-color: {self.palette().color(QtGui.QPalette.Window).name()};'
            '}')
        self.browse = QtWidgets.QPushButton('...')
        self.browse.setMaximumWidth(
            self.browse.fontMetrics().boundingRect('...').width() + 20
        )
        self.browse.clicked.connect(self._chooseImportFolder)
        self.registerField('libFolder', self.pathEdit)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.flightFolderLabel, 0, 0 ,1, 3)
        layout.addWidget(self.flightFolderBox, 0, 1, 1, 2)
        layout.addWidget(self.pathLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1)
        layout.addWidget(self.browse, 1, 2)
        layout.setColumnMinimumWidth(0, self.flightFolderLabel.minimumWidth())
        self.setLayout(layout)

    def initializePage(self):
        importFolderName = Path(self.field('importFolder')).name
        if importFolderName is not None:
            self.flightFolderBox.setText(importFolderName)

    def _chooseImportFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            'Import to ...',
            self.pathEdit.text(),
            QtWidgets.QFileDialog().ShowDirsOnly
        )

        if not folder == '':
            self.pathEdit.setText(folder)

    def nextId(self):
        return PageIds.Page_Conclusion
