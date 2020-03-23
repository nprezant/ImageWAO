
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
        # self.sourceModel.dataChanged.connect(self.) # TODO connect data changed to check if special layout needs to be displayed.
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

        # Default root path is $HOME$/Pictures/ImageWAO
        self._defaultRoot = str(Path.home() / 'Pictures/ImageWAO')
        self._nothingInRootLayout = None

        # Root path.
        settings = QtCore.QSettings()
        rootPath:str = settings.value(
            'library/homeDirectory',
            self._defaultRoot
        )

        # Validate that this is a proper directory.
        # If not, default to the _defaultRoot
        if not Path(rootPath).is_dir():
            rootPath = self._defaultRoot

        # Re-base the model on the new root path.
        self.rebase(rootPath)

    def setNothingInRootLayout(self, layout):
        '''
        This layout will be used when there are no folders in the root layout.
        '''
        self._noFoldersInRootLayout = layout

    def nothingInRootLayout(self):
        '''
        This layout will be shown when no folders are found in the root directory.
        The default layout simply informs the user that there are no folders.

        To set a custom layout, set one with `setNothingInRootLayout()`
        '''

        # If a custom layout has been set, use that.
        if self._nothingInRootLayout is not None:
            return self._nothingInRootLayout

        # No custom layout set, so return the default
        # prompt user to choose a flights folder
        label = QtWidgets.QLabel('There is nothing here :(')
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # add to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        return layout

    def setConditionalLayout(self):
        '''
        Sets the layout based on whether or not anything is found in the root directory.
        '''

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.address) # Address bar always shown

        # If things in root dir
        if not len([1 for _ in Path(self.rootPath).glob('**/*')]) == 0:
            layout.addWidget(self.proxyView, stretch=1)

        # Nothing in root dir
        else:
            layout.addLayout(self.nothingInRootLayout(), stretch=1)

        self.setLayout(layout)

    def changeRootFolderDialog(self):

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
            self.rebase(folder)

    def rebase(self, rootPath:str):
        '''
        Re-base the file system model off of `rootPath`.
        Raises ValueError if the path is not a directory.
        '''

        # Ensure root path exists
        self.rootPath = rootPath
        try:
            Path(self.rootPath).mkdir(exist_ok=True)
        except:
            raise ValueError(f'Invalid root directory: {rootPath}')

        # Ensure root path is directory
        if not Path(self.rootPath).is_dir():
            raise ValueError(f'Root path must be directory, not: {rootPath}')

        # Save this root path
        QtCore.QSettings().setValue('library/homeDirectory', rootPath)

        # file model and view
        self.sourceModel.setRootPath(self.rootPath)
        self.proxyView.setRootIndex(self._rootProxyIndex())

        # connection to update view window from view window interaction
        self.proxyView.activated.connect(self.viewActivated)

        # address bar
        self.address.home_path = self.sourceModel.rootDirectory()
        self.address.path = self.sourceModel.rootDirectory()

        # connection to update view window based on address bar
        self.address.activated.connect(self.addressActivated)

        # Set layout
        self.setConditionalLayout()

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
