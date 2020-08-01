from PySide2 import QtCore, QtWidgets, QtGui

from base import config
from tools import DirectoryValidator

from .ids import PageIds


class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Choose folder to import from")
        self.setSubTitle(
            "This wizard will help you import new (unsorted) "
            "aerial flight images and categorize them into their "
            "proper transects."
        )

        self.pathLabel = QtWidgets.QLabel("Import from:")
        self.pathEdit = QtWidgets.QLineEdit()
        self.pathEdit.setValidator(DirectoryValidator())
        self.pathEdit.textChanged.connect(lambda text: self.completeChanged.emit())
        self.pathEdit.textChanged.connect(
            lambda text: self._updateInvalidPathVisibility()
        )
        self.browse = QtWidgets.QPushButton("...")
        self.browse.setToolTip("Browse")
        self.browse.setMaximumWidth(
            self.browse.fontMetrics().boundingRect("...").width() + 20
        )
        self.browse.clicked.connect(self._chooseImportFolder)
        self.registerField("importFolder", self.pathEdit)

        self.invalidPathLabel = QtWidgets.QLabel(
            "Please enter a valid folder path or choose one with the browse button"
        )
        self.invalidPathLabel.setStyleSheet("QLabel { color: red }")

        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.pathLabel, 0, 0)
        layout.addWidget(self.pathEdit, 0, 1)
        layout.addWidget(self.browse, 0, 2)
        layout.addWidget(self.invalidPathLabel, 1, 0, 1, 3)
        self.setLayout(layout)

    def initializePage(self):
        self.pathEdit.setText(str(self._defaultImportFolder))

    @property
    def _defaultImportFolder(self):
        return config.flightImportFolder

    def _saveDefaults(self):
        # save default import path
        config.flightImportFolder = self.pathEdit.text()

    def _chooseImportFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            "Choose Import Folder",
            self.pathEdit.text(),
            QtWidgets.QFileDialog().ShowDirsOnly,
        )

        if not folder == "":
            self.pathEdit.setText(folder)

    def _updateInvalidPathVisibility(self):
        if self.pathEdit.hasAcceptableInput():
            self.invalidPathLabel.hide()
        else:
            self.invalidPathLabel.show()

    def isComplete(self):
        return self.pathEdit.hasAcceptableInput()

    def nextId(self):
        return PageIds.Page_Parameters
