
from pathlib import Path

from PySide2 import QtCore, QtGui, QtWidgets

from tools import clearLayout
from base import config

from .address import AddressBar
from .popup import LibraryMenu
from .events import DirectoryChangeEvent, EventTypes

class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    filterOut = None

    def filterAcceptsRow(self, sourceRow, sourceParent):
        # Fetch datetime value.
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        data = self.sourceModel().data(index)
        
        # Filter OUT matching files
        if self.filterOut is None:
            return super().filterAcceptsRow(sourceRow, sourceParent)
        elif self.filterOut.lower() in data.lower():
            return False
        else:
            return True
        

class Library(QtWidgets.QWidget):

    # Signals
    fileActivated = QtCore.Signal(str)
    directoryChanged = QtCore.Signal(str)

    # Events
    Events = EventTypes()

    def __init__(self):
        super().__init__()

        self.sourceModel = QtWidgets.QFileSystemModel()
        self.proxyModel = SortFilterProxyModel()
        self.proxyView = QtWidgets.QListView()

        self.proxyView.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.sourceModel)
        self.proxyModel.filterOut = Path(config.markedImageFolder).name

        self.address = AddressBar()

        # Context menu policy must be CustomContextMenu for us to implement
        # our own context menu. Connect the context menu request to our internal slot.
        self.menu = LibraryMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)

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
        self.sourceModel.setRootPath(self.rootPath)

        # file view
        self.proxyView.setRootIndex(self._rootProxyIndex())

        # connection to update view window from view window interaction
        self.proxyView.activated.connect(self.viewActivated)

        # address bar
        self.address.home_path = self.sourceModel.rootDirectory()
        self.address.path = self.sourceModel.rootDirectory()

        # connection to update view window based on address bar
        self.address.activated.connect(self.addressActivated)

        # layout init
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)

        # add layout items
        self.layout().addWidget(self.address)
        self.layout().addWidget(self.proxyView, stretch=1)

    def _rootProxyIndex(self):
        return self.proxyModel.mapFromSource(self.sourceModel.index(self.rootPath))

    @QtCore.Slot()
    def viewActivated(self, index):
        sourceIndex = self.proxyModel.mapToSource(index)
        if self.sourceModel.fileInfo(sourceIndex).isDir():
            QtCore.QCoreApplication.postEvent(self, DirectoryChangeEvent(index, sourceIndex))
        else:
            # Bubble up the path signal
            self.fileActivated.emit(self.sourceModel.filePath(sourceIndex))

    @QtCore.Slot()
    def addressActivated(self, path):
        index = self.proxyModel.mapFromSource(self.sourceModel.index(path))
        self.viewActivated(index)

    def customEvent(self, event):
        '''
        Handle the custom events. Namely, if the directory is changed.
        '''
        if event.type() == EventTypes.DirectoryChange:
            # If the directory change event was accepted, then by all means change the directory.
            index = event.proxyIndex
            sourceIndex = event.sourceIndex
            self.proxyView.setRootIndex(index)
            self.address.path = QtCore.QDir(self.sourceModel.filePath(sourceIndex))
            self.directoryChanged.emit(self.sourceModel.filePath(sourceIndex))

    @QtCore.Slot(list)
    def selectFiles(self, files):
        ''' Try to select all matching files in the library. '''

        # No files passed in
        if len(files) == 0:
            return

        # Clear current selection
        self.proxyView.selectionModel().clearSelection()

        # Get model indexes, convert to proxy
        indexes = [self.sourceModel.index(str(f)) for f in files]
        proxyIndexes = [self.proxyModel.mapFromSource(idx) for idx in indexes]

        # Select each index
        for idx in proxyIndexes:
            self.proxyView.selectionModel().select(idx, QtCore.QItemSelectionModel.Select)

        # Scroll to the first of the selected files
        self.proxyView.scrollTo(proxyIndexes[0])

    @QtCore.Slot(QtCore.QPoint)
    def _customMenuRequested(self, pos:QtCore.QPoint):
        '''
        Open the context menu with the currently selected item.
        '''

        # Find the selected files, and let the menu
        # know what they are
        selectionModel = self.proxyView.selectionModel()
        proxyIndexes = selectionModel.selectedIndexes()

        paths = []
        for idx in proxyIndexes:
            sourceIndex = self.proxyModel.mapToSource(idx)  
            paths.append(self.sourceModel.filePath(sourceIndex))

        if paths:
            self.menu.setTargetPaths(paths)
            self.menu.popup(self.mapToGlobal(pos))
