
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import (
    QMainWindow, QDockWidget, QMenu, QAction, QWizard
)

QCoreApplication.setOrganizationName('Namibia WAO')
QCoreApplication.setOrganizationDomain('imagewao.com')
QCoreApplication.setApplicationName('ImageWAO')

class QImageWAO(QMainWindow):

    def __init__(
        self,
        mspaint,
        grid,
        library,
        animalAdder,
        animalTotals,
        flightImportWizard,
    ):
        super().__init__()
        self.setCentralWidget(mspaint)
        self._setGrid(grid)
        self._setLibrary(library)
        self._setAnimalAdder(animalAdder)
        self._setAnimalTotals(animalTotals)

        self.flightImportWizard = flightImportWizard

        self._menusCreated = False
        self._makeMenus()

    def _setGrid(self, grid):
        self.grid = grid
        self.gridDock = QDockWidget('Image Grids', self)
        self.gridDock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.gridDock.setWidget(self.grid)
        self.addDockWidget(Qt.RightDockWidgetArea, self.gridDock)

    def _setLibrary(self, library):
        self.library = library
        self.libraryDock = QDockWidget('Library', self)
        self.libraryDock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.libraryDock.setWidget(self.library)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.libraryDock)

    def _setAnimalAdder(self, animal_adder):
        self.animalAdder = animal_adder
        self.animalAdderDock = QDockWidget('Add New Animal', self)
        self.animalAdderDock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.animalAdderDock.setWidget(self.animalAdder)
        self.addDockWidget(Qt.RightDockWidgetArea, self.animalAdderDock)

    def _setAnimalTotals(self, animal_totals):
        self.animalTotals = animal_totals
        self.animalTotalsDock = QDockWidget('Total Animal Counts', self)
        self.animalTotalsDock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.animalTotalsDock.setWidget(self.animalTotals)
        self.addDockWidget(Qt.RightDockWidgetArea, self.animalTotalsDock)

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
            self.fileMenu = QMenu('&File', self)
            self.viewMenu = QMenu('&View', self)
            self._menusCreated = True
        
    def _populateMenus(self):
        a3 = QAction('Import Flight Images', self)
        a3.triggered.connect(self.flightImportWizard.open)
        self.fileMenu.addAction(a3)

    def _arrangeMenus(self):
        self.menuBar().addMenu(self.fileMenu)
