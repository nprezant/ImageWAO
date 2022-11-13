from pathlib import Path

from PySide6 import QtCore, QtWidgets

from base import config

from .address import AddressBar
from .popup import LibraryMenu
from .events import DirectoryChangeEvent, EventTypes
from .sortfilterproxymodel import SortFilterProxyModel


class Library(QtWidgets.QWidget):

    # Signals
    fileSelected = QtCore.Signal(str)
    fileActivated = QtCore.Signal(str)
    directoryChanged = QtCore.Signal(str)
    showFlightInfoRequested = QtCore.Signal(str)
    showMigrationLogRequested = QtCore.Signal(str)
    showDistributionFormRequested = QtCore.Signal(str)

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
        self.proxyModel.filterOut.append(config.markedImageFolderName.lower())
        self.proxyModel.filterOut.append(config.imageWaoMetaFolderName.lower())
        self.proxyModel.filterOut.append(config.flightDataFolderName.lower())

        self.address = AddressBar()

        # When the root path changes, we'll need to update the file watcher
        self.sourceModel.rootPathChanged.connect(self._changeWatchedPath)

        # When the file watcher has the directory change, we'll want to *maybe* update the layout
        self.watcher.directoryChanged.connect(self.setConditionalLayout)
        self.watcher.fileChanged.connect(self.setConditionalLayout)

        # Context menu policy must be CustomContextMenu for us to implement
        # our own context menu. Connect the context menu request to our internal slot.
        self.menu: LibraryMenu = LibraryMenu(self)
        self.menu.showFlightInfoRequested.connect(self.showFlightInfoRequested.emit)
        self.menu.showMigrationLogRequested.connect(self.showMigrationLogRequested.emit)
        self.menu.showDistributionFormRequested.connect(
            self.showDistributionFormRequested.emit
        )
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._customMenuRequested)

        # For optimization purposes, determining the proper layout
        self._rootDirPreviouslyBlank = None

        # Handle selection changes and map to appropriate signals
        self.proxyView.selectionModel().selectionChanged.connect(
            self._handleSelectionChange
        )

        # Root path. Defaults to $HOME$/Pictures/ImageWAO
        rootPath: str = config.libraryDirectory

        # Widget for use when there are no folders
        label = QtWidgets.QLabel(
            "  There is nothing here :(  \n  Right click to import flight images  "
        )
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # add to layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label, stretch=1)

        # Make widget with this layout
        self.noFoldersWidget = QtWidgets.QWidget()
        self.noFoldersWidget.setLayout(layout)

        # Widget for use when there are folders
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.address)
        layout.addWidget(self.proxyView, stretch=1)
        self.hasFoldersWidget = QtWidgets.QWidget()
        self.hasFoldersWidget.setLayout(layout)

        # Create the stacked layout
        self.stackedLayout = QtWidgets.QStackedLayout()
        self.setLayout(self.stackedLayout)
        self.stackedLayout.addWidget(self.noFoldersWidget)
        self.stackedLayout.addWidget(self.hasFoldersWidget)

        # Re-base the model on the new root path.
        self.rebase(rootPath)

    @QtCore.Slot(str)
    def _changeWatchedPath(self, fp):
        """
        Change the watched path to `fp`. Removes all other paths.
        """
        files = self.watcher.files()
        dirs = self.watcher.directories()
        if files:
            self.watcher.removePaths(files)
        if dirs:
            self.watcher.removePaths(dirs)
        self.watcher.addPath(fp)

    def changeRootFolderDialog(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            "Choose Flight Folder",
            Path().home().anchor,
            QtWidgets.QFileDialog().ShowDirsOnly,
        )

        if not folder == "":

            # rebase view on new folder
            self.rebase(folder)

    def rebase(self, rootPath: str):
        """
        Re-base the file system model off of `rootPath`.
        Raises ValueError if the path is not a directory.
        """

        # Ensure root path exists
        self.rootPath = rootPath
        try:
            Path(self.rootPath).mkdir(exist_ok=True)
        except FileNotFoundError:
            raise ValueError(f"Invalid root directory: {rootPath}")

        # Ensure root path is directory
        if not Path(self.rootPath).is_dir():
            raise ValueError(f"Root path must be directory, not: {rootPath}")

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

    @QtCore.Slot(str)
    def setConditionalLayout(self, path: str = None):
        """
        Sets the layout based on whether or not anything is found in the root directory.
        """

        # If we are not currently in the root, nothing to do.
        if not self._inRootIndex():
            return

        # If things in root dir
        rootPath = Path(self.rootPath)
        rootDirBlank = (
            len(
                [
                    1
                    for fp in rootPath.glob("**/*")
                    if not fp.relative_to(rootPath).parts[0][0] == "."
                ]
            )
            == 0
        )

        # If this is the same situation as last time we checked, nothing to do
        # (for optimization)
        if self._rootDirPreviouslyBlank is None:
            pass
        elif self._rootDirPreviouslyBlank == rootDirBlank:
            return

        # Record whether anything is in the root directory
        self._rootDirPreviouslyBlank = rootDirBlank

        if rootDirBlank:
            self.stackedLayout.setCurrentWidget(self.noFoldersWidget)
        else:
            self.stackedLayout.setCurrentWidget(self.hasFoldersWidget)

    def _rootProxyIndex(self):
        return self.proxyModel.mapFromSource(self.sourceModel.index(self.rootPath))

    def _inRootIndex(self):
        """True if the current view index is the model root index"""
        return self._rootProxyIndex() == self.proxyView.rootIndex()

    def _inFolderLevel(self, level: int):
        """True if we are currently in the folder level specified.
        0 is root index. 1 in one folder down, etc.
        """
        actualRoot = Path(
            self.sourceModel.filePath(
                self.proxyModel.mapToSource(self._rootProxyIndex())
            )
        )

        currentRoot = Path(
            self.sourceModel.filePath(
                self.proxyModel.mapToSource(self.proxyView.rootIndex())
            )
        )

        compareRoot = currentRoot
        for _ in range(level):
            compareRoot = compareRoot.parent

        return actualRoot == compareRoot

    @QtCore.Slot()
    def viewActivated(self, index):
        sourceIndex = self.proxyModel.mapToSource(index)
        if self.sourceModel.fileInfo(sourceIndex).isDir():
            QtCore.QCoreApplication.postEvent(
                self, DirectoryChangeEvent(index, sourceIndex)
            )
            self.proxyView.clearSelection()  # Clear selection on directory change
        else:
            # Bubble up the path signal
            self.fileActivated.emit(self.sourceModel.filePath(sourceIndex))

    @QtCore.Slot()
    def addressActivated(self, path):
        index = self.proxyModel.mapFromSource(self.sourceModel.index(path))
        self.viewActivated(index)

    def customEvent(self, event):
        """
        Handle the custom events. Namely, if the directory is changed.
        """
        if event.type() == EventTypes.DirectoryChange:
            # If the directory change event was accepted, then by all means change the directory.
            index = event.proxyIndex
            sourceIndex = event.sourceIndex
            self.proxyView.setRootIndex(index)
            self.address.path = QtCore.QDir(self.sourceModel.filePath(sourceIndex))
            self.directoryChanged.emit(self.sourceModel.filePath(sourceIndex))

    @QtCore.Slot(list)
    def selectFiles(self, files):
        """ Try to select all matching files in the library. """

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
            self.proxyView.selectionModel().select(
                idx, QtCore.QItemSelectionModel.Select
            )

        # Scroll to the first of the selected files
        self.proxyView.scrollTo(proxyIndexes[0])

    @QtCore.Slot(QtCore.QPoint)
    def _customMenuRequested(self, pos: QtCore.QPoint):
        """
        Open the context menu with the currently selected item.
        """

        # The position given is with respect to the parent widget.
        # Need to convert it to the local viewport position.
        gp = self.mapToGlobal(pos)
        lp = self.proxyView.viewport().mapFromGlobal(gp)

        # Find the file under the mouse
        idx = self.proxyView.indexAt(lp)
        srcIndex = self.proxyModel.mapToSource(idx)
        path = self.sourceModel.filePath(srcIndex)

        # We should be able to open the flight import wizard by right clicking anywhere
        # so long as we are in the root index
        if self._inRootIndex():
            self.menu.enableImportWizard()

        if path:
            self.menu.setTargetPath(path)  # enables reveal in explorer action

            if self._inRootIndex():
                self.menu.enableShowFlightInfo()
                self.menu.enableShowDistributionForm()

            if self._inFolderLevel(1):
                self.menu.enableShowMigrationLog()

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
            path: str = self.sourceModel.filePath(srcIndex)
            self.fileSelected.emit(path)
