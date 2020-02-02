
from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import (
    QMainWindow, QDockWidget
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
        animal_adder,
        animal_totals,
    ):
        super().__init__()
        self.setCentralWidget(mspaint)
        self._setGrid(grid)
        self._setLibrary(library)
        self._setAnimalAdder(animal_adder)
        self._setAnimalTotals(animal_totals)

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
