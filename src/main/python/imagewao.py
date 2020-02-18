
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

        # The image editor is the central widget
        self.setCentralWidget(mspaint)
        self.viewer = mspaint

        # Dock widgets are saved in a dictionary
        self._dockWidgets = {}

        # Dock widget references
        self.grid = grid
        self.library = library
        self.animalAdder = animalAdder
        self.animalTotals = animalTotals

        # Dock widget creation
        self._addDockWidget(self.grid, 'Image Grids', startArea=QtCore.Qt.RightDockWidgetArea)
        self._addDockWidget(self.library, 'Library', startArea=QtCore.Qt.LeftDockWidgetArea)
        self._addDockWidget(self.animalAdder, 'Animal Adder', startArea=QtCore.Qt.RightDockWidgetArea)
        self._addDockWidget(self.animalTotals, 'Animal Totals', startArea=QtCore.Qt.RightDockWidgetArea)

        # Hide unused dock widgets
        self._dockWidgets['Animal Adder'].hide()
        self._dockWidgets['Animal Totals'].hide()

        # Wizards
        self.importWizards = importWizards

        # Notifications
        self.notifier = notifier
        self.notifier.parent = self

        # Progress Bar
        self.progressBar = progressBar

        # Connections
        self.library.fileActivated.connect(self._updateGridSelection)
        self.library.directoryChanged.connect(self._setGridImages)

        self.grid.model().progress.connect(self.progressBar.setValue)

        self.grid.selectedIndexesChanged.connect(self._updateViewerFromGrid)
        self.grid.selectedIndexesChanged.connect(self._updateLibraryFromGrid)

        # File | Etc. Menus
        self._menusCreated = False
        self._makeMenus()

    def _updateLibraryFromGrid(self, indexes):
        files = [idx.data(role=UserRoles.ImagePath) for idx in indexes]
        self.library.selectFiles(files)

    def _setGridImages(self, path):
        self.grid.model().tryAddFolder(path)

    def _updateViewerFromGrid(self, indexes):
        try:
            index = indexes[0]
        except IndexError:
            pass
        else:
            if index.isValid():
                self.viewer.setImage(index.data(role=UserRoles.EntireImage))

    def _updateGridSelection(self, path):
        self.grid.selectFile(path)

    def _addDockWidget(self, w, name:str, areas=QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea, startArea=QtCore.Qt.LeftDockWidgetArea):
        dock = QtWidgets.QDockWidget(name, self)
        dock.setAllowedAreas(areas)
        dock.setWidget(w)
        self.addDockWidget(startArea, dock)
        self._dockWidgets[name] = dock

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
