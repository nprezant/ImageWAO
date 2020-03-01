
from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from .address import AddressBar
from tools import clearLayout


class Library(QtWidgets.QWidget):

    fileActivated = QtCore.Signal(str)
    directoryChanged = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        self.model = QtWidgets.QFileSystemModel()
        self.view = QtWidgets.QListView()
        self.address = AddressBar()

        # root path
        settings = QtCore.QSettings()
        self.rootPath = settings.value(
            'library/homeDirectory',
            None
        )

        if self.rootPath is None:
            self.pathNotDefined()
        else:
            self.rebase()

    def pathNotDefined(self):
        
        # prompt user to choose a flights folder
        button = QtWidgets.QPushButton('Choose Flights Folder')
        button.clicked.connect(self.chooseRootFolder)

        # add to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

    def chooseRootFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            'Choose Flight Folder',
            Path().home().anchor,
            QtWidgets.QFileDialog().ShowDirsOnly
        )

        if not folder == '':

            # remove old layout
            clearLayout(self.layout())

            # rebase view on new folder
            self.rootPath = folder
            self.rebase()

            # save this root path
            QtCore.QSettings().setValue('library/homeDirectory', folder)

    def rebase(self):

        # file model
        self.model.setRootPath(self.rootPath)

        # file view
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(self.rootPath))

        # connection to update view window from view window interaction
        self.view.activated.connect(self.viewActivated)

        # address bar
        self.address.home_path = self.model.rootDirectory()
        self.address.path = self.model.rootDirectory()

        # connection to update view window based on address bar
        self.address.activated.connect(self.addressActivated)

        # layout init
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        # add layout items
        self.layout().addWidget(self.address)
        self.layout().addWidget(self.view, stretch=1)

    def viewActivated(self, index):
        if self.model.fileInfo(index).isDir():
            self.view.setRootIndex(index)
            self.address.path = QtCore.QDir(self.model.filePath(index))
            self.directoryChanged.emit(self.model.filePath(index))
        else:
            # Bubble up the path signal
            self.fileActivated.emit(self.model.filePath(index))

    def addressActivated(self, path):
        index = self.model.index(path)
        self.viewActivated(index)

    def selectFiles(self, files):
        ''' Try to select all matching files in the library. '''

        # No files passed in
        if len(files) == 0:
            return

        # Clear current selection
        self.view.selectionModel().clearSelection()

        # Get model indexes
        indexes = [self.model.index(str(f)) for f in files]

        # Select each index
        for idx in indexes:
            self.view.selectionModel().select(idx, QtCore.QItemSelectionModel.Select)

        # Scroll to the first of the selected files
        self.view.scrollTo(indexes[0])
