"""
Popup menu for the library and address bars.
"""

import sys
from PySide6 import QtWidgets, QtCore

from tools import showInFolder

from ..flightimport import FlightImportWizard


class LibraryMenu(QtWidgets.QMenu):
    """
    Note: You must call setTargetPaths for the context
    menu to populate.
    """

    showFlightInfoRequested = QtCore.Signal(str)  # flight folder
    showMigrationLogRequested = QtCore.Signal(str)  # transect folder
    showDistributionFormRequested = QtCore.Signal(str)  # flight folder

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.revealAction = None
        self.importWizardAction = None
        self.showFlightInfoAction = None
        self.showMigrationLogAction = None
        self.showDistributionFormAction = None

        self._targetPath = ""

    def reset(self):
        self.revealAction = None
        self.importWizardAction = None
        self.showFlightInfoAction = None
        self.showMigrationLogAction = None
        self.showDistributionFormAction = None

    def setTargetPath(self, path: str):
        """
        This menu is based off of target paths.
        The context buttons will populate automatically.
        """

        self._targetPath = path

        # Create menu actions
        if sys.platform == "win32":
            self.revealAction = QtWidgets.QAction("Show in Explorer", self.parent())
        elif sys.platform == "darwin":
            self.revealAction = QtWidgets.QAction("Reveal in Finder", self.parent())
        else:
            self.revealAction = QtWidgets.QAction("Show file", self.parent())

        # Connect handlers for actions
        self.revealAction.triggered.connect(lambda: showInFolder(path))

    def enableImportWizard(self):
        """
        Creates the import wizard action. Will be added to the menu during `popup()`
        """
        self.importWizardAction = QtWidgets.QAction("Import new images", self.parent())
        self.importWizardAction.triggered.connect(FlightImportWizard.openNew)

    def enableShowFlightInfo(self):
        """
        Creates the action to show the flight info dialog.
        Will be added to the menu during popup()
        """
        self.showFlightInfoAction = QtWidgets.QAction("Flight info", self.parent())
        self.showFlightInfoAction.triggered.connect(
            lambda: self.showFlightInfoRequested.emit(self._targetPath)
        )

    def enableShowMigrationLog(self):
        """
        Creates the action to show the migration log dialog.
        Will be added to the menu during popup()
        """
        self.showMigrationLogAction = QtWidgets.QAction("Migration log", self.parent())
        self.showMigrationLogAction.triggered.connect(
            lambda: self.showMigrationLogRequested.emit(self._targetPath)
        )

    def enableShowDistributionForm(self):
        """
        Creates the action to show the distribution form.
        Will be added to the menu during popup()
        """
        self.showDistributionFormAction = QtWidgets.QAction(
            "Distribute flight", self.parent()
        )
        self.showDistributionFormAction.triggered.connect(
            lambda: self.showDistributionFormRequested.emit(self._targetPath)
        )

    def popup(self, *args):
        """
        Re-implemented to show popup menu.
        Menu actions populate based on which actions have been set.
        """

        self.clear()

        if self.revealAction is not None:
            self.addAction(self.revealAction)
            self.addSeparator()

        if self.importWizardAction is not None:
            self.addAction(self.importWizardAction)
            self.addSeparator()

        if self.showDistributionFormAction is not None:
            self.addAction(self.showDistributionFormAction)

        if self.showFlightInfoAction is not None:
            self.addAction(self.showFlightInfoAction)

        if self.showMigrationLogAction is not None:
            self.addAction(self.showMigrationLogAction)

        self.reset()
        return super().popup(*args)
