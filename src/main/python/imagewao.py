
from PySide2 import QtGui, QtCore, QtWidgets

from gridview import UserRoles

QtCore.QCoreApplication.setOrganizationName('Namibia WAO')
QtCore.QCoreApplication.setOrganizationDomain('imagewao.com')
QtCore.QCoreApplication.setApplicationName('ImageWAO')

class QImageWAO(QtWidgets.QMainWindow):

    def __init__(
        self,
        mspaint,
        grid,
        library,
        animalAdder,
        animalTotals,
        importWizards,
        notifier,
        progressBar,
    ):
        super().__init__()
        self.setCentralWidget(mspaint)
        self._setGrid(grid)
        self._setLibrary(library)
        self._setAnimalAdder(animalAdder)
        self._setAnimalTotals(animalTotals)

        self.viewer = mspaint
        self.importWizards = importWizards
        self.notifier = notifier
        self.notifier.parent = self
        self.progressBar = progressBar

        # Connections
        self.library.activated.connect(self._setViewerImage)
        self.library.directoryChanged.connect(self._setGridImages)

        self.grid.model().progress.connect(self.progressBar.setValue)

        self.grid.selectedIndexesChanged.connect(self._updateViewerFromGrid)
        self.grid.selectedIndexesChanged.connect(self._updateLibraryFromGrid)

        self._menusCreated = False
        self._makeMenus()

    def _updateLibraryFromGrid(self, indexes):
        files = [idx.data(role=UserRoles.ImagePath) for idx in indexes]
        self.library.selectFiles(files)

    def _setGridImages(self, path):
        self.grid.model().tryAddFolder(path)

    def _updateViewerFromGrid(self, indexes):
        index = indexes[0]
        if index.isValid():
            self.viewer.setImage(index.data(role=UserRoles.EntireImage))

    def _setViewerImage(self, path):
        pixmap = QtGui.QPixmap(path)
        self.viewer.setImage(pixmap)

    def _setGrid(self, grid):
        self.grid = grid
        self.gridDock = QtWidgets.QDockWidget('Image Grids', self)
        self.gridDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.gridDock.setWidget(self.grid)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.gridDock)

    def _setLibrary(self, library):
        self.library = library
        self.libraryDock = QtWidgets.QDockWidget('Library', self)
        self.libraryDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.libraryDock.setWidget(self.library)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.libraryDock)

    def _setAnimalAdder(self, animal_adder):
        self.animalAdder = animal_adder
        self.animalAdderDock = QtWidgets.QDockWidget('Add New Animal', self)
        self.animalAdderDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.animalAdderDock.setWidget(self.animalAdder)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.animalAdderDock)

    def _setAnimalTotals(self, animal_totals):
        self.animalTotals = animal_totals
        self.animalTotalsDock = QtWidgets.QDockWidget('Total Animal Counts', self)
        self.animalTotalsDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.animalTotalsDock.setWidget(self.animalTotals)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.animalTotalsDock)

    def _createActions(self):
        pass

    def _makeMenus(self):
        self._createMenus()
        self._clearMenus()
        self._populateMenus()
        self._arrangeMenus()

    def _clearMenus(self):
        self.fileMenu.clear()
        self.viewMenu.clear()

    def _createMenus(self):
        if self._menusCreated == False:
            self.fileMenu = QtWidgets.QMenu('&File', self)
            self.viewMenu = QtWidgets.QMenu('&View', self)
            self._menusCreated = True
        
    def _populateMenus(self):
        a = QtWidgets.QAction('Import Flight Images', self)
        a.triggered.connect(self.importWizards.openNewFlight)
        self.fileMenu.addAction(a)

        action = QtWidgets.QAction('Notify test', self)
        action.setShortcut('Ctrl+n')
        action.triggered.connect(
            lambda:
            self.notifier.notify('Whey 2 go!'))
        self.fileMenu.addAction(action)

    def _arrangeMenus(self):
        self.menuBar().addMenu(self.fileMenu)
