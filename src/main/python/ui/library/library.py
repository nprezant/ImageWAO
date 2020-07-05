
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
    fileSelected = QtCore.Signal(str)
    fileActivated = QtCore.Signal(str)
    directoryChanged = QtCore.Signal(str)

    # Events
    Events = EventTypes()

    def __init__(self):
        super().__init__()

        self.sourceModel = QtWidgets.QFileSystemModel()
        self.watcher = QtCore.QFileSystemWatcher()
        self.proxyModel = SortFilterProxyModel()
        self.proxyView = QtWidgets.QListView()

        self.proxyView.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.sourceModel)
        self.proxyModel.filterOut = Path(config.markedImageFolder).name

        self.address = AddressBar()

        # When the root path changes, we'll need to update the file watcher
        self.sourceModel.rootPathChanged.connect(self._changeWatchedPath)

        # When the file watcher has the directory change, we'll want to *maybe* update the layout
        self.watcher.directoryChanged.connect(self.setConditionalLayout)
        self.watcher.fileChanged.connect(self.setConditionalLayout)

        # Context menu policy must be CustomContextMenu for us to implement
        # our own context menu. Connect the context menu request to our internal slot.
        self.menu = LibraryMenu(self)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)

        # For optimization purposes, determining the proper layout
        self._rootDirPreviouslyBlank = None

        # Handle selection changes and map to appropriate signals
        self.proxyView.selectionModel().selectionChanged.connect(self._handleSelectionChange)

        # Allows different layouts based on whether or not the folder is empty
        self._nothingInRootLayout = None

        # Root path. Defaults to $HOME$/Pictures/ImageWAO
        rootPath:str = config.libraryDirectory

        # Re-base the model on the new root path.
        self.rebase(rootPath)

    @QtCore.Slot(str)
    def _changeWatchedPath(self, fp):
        '''
        Change the watched path to `fp`. Removes all other paths.
        '''
        files = self.watcher.files()
        dirs = self.watcher.directories()
        if files:
            self.watcher.removePaths(files)
        if dirs:
            self.watcher.removePaths(dirs)
        self.watcher.addPath(fp)

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
        label = QtWidgets.QLabel('  There is nothing here :(  \n  Right click to import flight images  ')
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # add to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        return layout

    @QtCore.Slot(str)
    def setConditionalLayout(self, path:str=None):
        '''
        Sets the layout based on whether or not anything is found in the root directory.
        '''

        # If we are not currently in the root, nothing to do.
        if not self._inRootIndex():
            return

        # If things in root dir
        rootDirBlank = len([1 for _ in Path(self.rootPath).glob('**/*')]) == 0
        
        # If this is the same situation as last time we checked, nothing to do
        if self._rootDirPreviouslyBlank is None:
            pass
        elif self._rootDirPreviouslyBlank == rootDirBlank:
            return

        # Record whether anything is in the root directory
        self._rootDirPreviouslyBlank = rootDirBlank

        # Reparent current layout so we can use a new one
        if self.layout() is not None:
            
            # Get a reference to the layout's items so we don't lose them to the garbage collector
            # There should be two items: address bar, main item
            keepIndexes = [] # Track which indexes to keep references to
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if not item:
                    continue

                w = item.widget()
                if w:
                    if w is self.address or w is self.proxyView:
                        keepIndexes.append(i)
                    else:
                        pass

            # Taking the items that we want to keep out of the 
            # layout will maintain their references, because otherwise they'll
            # be deleted when we re-parent the layout.
            keepIndexes.sort(reverse=True)
            for i in keepIndexes:
                item = self.layout().takeAt(i)
                item.widget().hide()

            QtWidgets.QWidget().setLayout(self.layout())

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Add the address bar on top. Always shown.
        layout.addWidget(self.address)
        self.address.show()

        # If root dir has files or folders
        if not rootDirBlank:
            layout.addWidget(self.proxyView, stretch=1)
            self.proxyView.show()

        # Nothing in root dir
        else:
            layout.addLayout(self.nothingInRootLayout(), stretch=1)

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
        config.libraryDirectory = rootPath

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

    def _inRootIndex(self):
        '''True if the current view index is the model root index'''
        return self._rootProxyIndex() == self.proxyView.rootIndex()

    @QtCore.Slot()
    def viewActivated(self, index):
        sourceIndex = self.proxyModel.mapToSource(index)
        if self.sourceModel.fileInfo(sourceIndex).isDir():
            QtCore.QCoreApplication.postEvent(self, DirectoryChangeEvent(index, sourceIndex))
            self.proxyView.clearSelection() # Clear selection on directory change
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

        # The position given is with respect to the parent widget.
        # Need to convert it to the local viewport position.
        gp = self.mapToGlobal(pos)
        lp = self.proxyView.viewport().mapFromGlobal(gp)
        
        # Find the file under the mouse
        idx = self.proxyView.indexAt(lp)
        srcIndex = self.proxyModel.mapToSource(idx)
        path = self.sourceModel.filePath(srcIndex)

        if path:
            self.menu.setTargetPath(path)

        # We should be able to open the flight import wizard by right clicking anywhere
        # so long as we are in the root index
        if self._inRootIndex():
            self.menu.enableImportWizard()

        # Show the menu
        self.menu.popup(self.mapToGlobal(pos))

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def _handleSelectionChange(self, selected, deselected):
        model = self.proxyView.selectionModel()
        indexes = model.selectedIndexes()

        # Nothing to do if there are no indexes selected
        if len(indexes) == 0:
            return

        # Emit the first of the selected files
        index = indexes[0]
        if index.isValid():
            srcIndex = self.proxyModel.mapToSource(index)
            path:str = self.sourceModel.filePath(srcIndex)
            self.fileSelected.emit(path)
