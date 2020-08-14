from pathlib import Path

from PySide2 import QtGui, QtCore, QtWidgets

from base import ctx
from migrator import Migrator
from ui import (
    DockWidget,
    TitleBarText,
    StatusBar,
    LoadingOverlay,
    Notifier,
    Library,
    FlightImportWizard,
    QImageGridView,
    QImageEditor,
    CountTotals,
    DoYouWantToSave,
    FlightInfoForm,
    MigrationLogForm,
    DistributionForm,
    PreferencesDialog,
)

QtCore.QCoreApplication.setOrganizationName("Namibia WAO")
QtCore.QCoreApplication.setOrganizationDomain("imagewao.com")
QtCore.QCoreApplication.setApplicationName("ImageWAO")


class QImageWAO(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Read build settings
        self.version = ctx.build_settings["version"]

        # Migrate if necessary
        Migrator().migrate()

        # Whether or not the application has changes
        self._dirty = False

        # Window icon
        self.setWindowIcon(ctx.icon("icons/winIcon.png"))

        # Title bar text is managed
        self.titleBarText = TitleBarText(ctx.app.applicationName())
        self.titleBarText.changed.connect(self.setWindowTitle)

        # The image editor is the central widget
        self.imageViewer = QImageEditor()
        self.setCentralWidget(self.imageViewer)

        # Dock widget references
        self.imageGridView = QImageGridView()
        self.library = Library()
        self.countTotals = CountTotals()
        self.flightInfoForm = FlightInfoForm.CreateWithApplyCancel()
        self.migrationLogForm = MigrationLogForm()
        self.distributionForm = DistributionForm()

        # Dock widget creation
        self._addDockWidget(
            self.library,
            ctx.explorerIcon,
            "Flight Explorer",
            startArea=QtCore.Qt.LeftDockWidgetArea,
        )
        self._addDockWidget(
            self.imageGridView,
            ctx.defaultDockIcon,
            "Image Grids",
            startArea=QtCore.Qt.RightDockWidgetArea,
        )
        self._addDockWidget(
            self.countTotals,
            ctx.defaultDockIcon,
            "Count Totals",
            startArea=QtCore.Qt.LeftDockWidgetArea,
        )
        self.flightInfoDock = self._addDockWidget(
            self.flightInfoForm,
            ctx.defaultDockIcon,
            "Flight Info",
            startArea=QtCore.Qt.BottomDockWidgetArea,
            startVisible=False,
            startFloating=True,
        )
        self.migrationLogDock = self._addDockWidget(
            self.migrationLogForm,
            ctx.defaultDockIcon,
            "Migration Log",
            startArea=QtCore.Qt.BottomDockWidgetArea,
            startVisible=False,
            startFloating=True,
        )
        self.distributionDock = self._addDockWidget(
            self.distributionForm,
            ctx.defaultDockIcon,
            "Flight Distribution",
            startArea=QtCore.Qt.BottomDockWidgetArea,
            startVisible=False,
            startFloating=True,
        )

        # Event filters
        self.library.installEventFilter(self)

        # Notifications
        self.notifier = Notifier(self)

        # Status bar
        self.setStatusBar(StatusBar(self))

        # Loading overlay screen
        self.loadingOverlay = LoadingOverlay(self)
        self.loadingOverlay.hide()

        # Send initializing signals
        self.countTotals.readDirectory(self.library.rootPath)

        # Flight library signal connections
        self.library.fileSelected.connect(self.countTotals.selectFile)
        self.library.fileActivated.connect(self.imageGridView.selectFile)
        self.library.directoryChanged.connect(self.imageGridView.addFolder)
        self.library.directoryChanged.connect(self.titleBarText.setFolderName)
        self.library.directoryChanged.connect(self.countTotals.readDirectory)
        self.library.showFlightInfoRequested.connect(self._showFlightInfoDock)
        self.library.showMigrationLogRequested.connect(self._showMigrationLogDock)
        self.library.showDistributionFormRequested.connect(self._showDistributionDock)

        # Image grid signal connections
        self.imageGridView.loadProgress.connect(self.loadingOverlay.setProgress)
        self.imageGridView.loadFinished.connect(self.loadingOverlay.fadeOut)
        self.imageGridView.selectedImageChanged.connect(self.imageViewer.setImage)
        self.imageGridView.selectedFilesChanged.connect(self.library.selectFiles)
        self.imageGridView.notificationMessage.connect(self.notifier.notify)
        self.imageGridView.statusMessage.connect(self.showStatusMessage)
        self.imageGridView.countDataChanged.connect(self.countTotals.setTransectData)

        # Image viewer signal connections
        self.imageViewer.drawnItemsChanged.connect(self.imageGridView.setDrawings)
        self.imageViewer.drawnItemsChanged.connect(self._markAsDirty)

        # Count totals form connections
        self.countTotals.fileActivated.connect(self.imageGridView.selectFile)
        self.countTotals.selectedFilesChanged.connect(self.library.selectFiles)
        self.countTotals.requestDrawingUpdate.connect(
            self.imageGridView.save
        )  # Hacky. Ideally you could request the data without saving.

        # Flight info form signals
        self.flightInfoForm.closeRequested.connect(self.flightInfoDock.hide)
        self.migrationLogForm.closeRequested.connect(self.migrationLogDock.hide)

        # File | Etc. Menus
        fileMenu = self._createFileMenu()
        expMenu = self._createExperimentalMenu()
        infoMenu = self._createInfoMenu()

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addMenu(expMenu)
        self.menuBar().addMenu(infoMenu)

        # Toolbars
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.imageViewer.toolbar)

    @QtCore.Slot(tuple)
    def showStatusMessage(self, args):
        self.statusBar().showMessage(*args)

    @QtCore.Slot(str)
    def _showFlightInfoDock(self, flightFolder: str):
        fp = Path(flightFolder)
        self.flightInfoForm.readFlightFolder(fp)
        self.flightInfoDock.setTitleBarText(f"Flight Info - {fp.name}")
        self.flightInfoDock.show()

    @QtCore.Slot(str)
    def _showMigrationLogDock(self, transectFolder: str):
        fp = Path(transectFolder)
        self.migrationLogForm.readTransectFolder(fp)
        self.migrationLogDock.setTitleBarText(
            f"Migration Log - {fp.parent.name}/{fp.name}"
        )
        self.migrationLogDock.show()

    @QtCore.Slot(str)
    def _showDistributionDock(self, flightFolder: str):
        fp = Path(flightFolder)
        self.distributionForm.readFlightFolder(fp)
        self.distributionDock.setTitleBarText(f"Distribute flight - {fp.name}")
        self.distributionDock.show()

    def _addDockWidget(
        self,
        w,
        icon,
        name: str,
        startArea=QtCore.Qt.LeftDockWidgetArea,
        startVisible=True,
        startFloating=False,
    ) -> DockWidget:
        dock = DockWidget(name, icon, parent=self)
        dock.setWidget(w)
        dock.setVisible(startVisible)
        dock.setFloating(startFloating)
        dock.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | startArea
        )
        self.addDockWidget(startArea, dock)
        return dock

    def _createFileMenu(self) -> QtWidgets.QMenu:

        menu = QtWidgets.QMenu("&File", self)

        # File Menu
        a = QtWidgets.QAction("Save", self)
        a.setShortcut("Ctrl+S")
        a.triggered.connect(self._saveIfDirty)
        menu.addAction(a)

        a = QtWidgets.QAction("Import Flight Images", self)
        a.triggered.connect(FlightImportWizard().openNew)
        menu.addAction(a)

        menu.addSeparator()

        a = QtWidgets.QAction("Preferences", self)
        a.triggered.connect(self._showPreferencesForm)
        menu.addAction(a)

        return menu

    def _createExperimentalMenu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu("&Exp.", self)

        a = QtWidgets.QAction("Test notification", self)
        a.setShortcut("Ctrl+N")
        a.triggered.connect(lambda: self.notifier.notify(""))
        menu.addAction(a)

        a = QtWidgets.QAction("Reset settings", self)
        a.triggered.connect(lambda: QtCore.QSettings().clear())
        menu.addAction(a)

        a = QtWidgets.QAction("Throw runtime error", self)
        a.triggered.connect(self._raiseError)
        menu.addAction(a)

        return menu

    def _createInfoMenu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu("&Info", self)
        menu.addAction(QtWidgets.QAction(f"Version: {self.version}", self))
        return menu

    def _saveIfDirty(self):
        if self._dirty:
            self.save()

    def save(self):
        """
        All save operations. Once saving is completed,
        The application will be marked clean.
        """
        self.imageGridView.save()
        self._markAsClean()

    def _markAsDirty(self, *args):
        """
        Any signals that signify save-able changes were made
        should also connect to this slot, which will mark the
        application as "dirty" such that the user will
        be prompted to save before exiting the application.
        """
        self._dirty = True
        self.titleBarText.setDirty(True)

    def _markAsClean(self):
        """
        This operation resets the _dirty flag and also updates the
        title bar to the clean state.
        """
        self._dirty = False
        self.titleBarText.setDirty(False)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        """
        Catch library change events and see if the application needs to save
        before accepting them.
        """
        if obj == self.library:
            if event.type() == Library.Events.DirectoryChange:
                self._exitDirectoryEvent(event)

                # If we are going to change the directory, we'll need to clear
                # the images from the grid and from the viewer.
                if event.isAccepted():
                    self.imageGridView.clear()
                    self.imageViewer.clear()
                    return False  # Don't filter it, allow to progate
                else:
                    return True  # Filter this one! Don't let the dir change

        return super().eventFilter(obj, event)

    def _exitDirectoryEvent(self, event: QtCore.QEvent):
        """
        Ensures that changes are saved (or intentionally ignored)
        when a directory changes.
        """
        # If there are no changes,
        # simply accept the event.
        if not self._dirty:
            event.accept()
            return

        # Based on user response, either save, don't save,
        # or quit.
        ret = DoYouWantToSave().exec_()
        if ret == QtWidgets.QMessageBox.Save:
            self.save()
            event.accept()
        elif ret == QtWidgets.QMessageBox.Discard:
            self._markAsClean()
            event.accept()
        elif ret == QtWidgets.QMessageBox.Cancel:
            event.ignore()
        else:
            # Should never be reached
            event.ignore()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        Check to ensure that changes are saved if
        the user wants to save them.
        """
        self._exitDirectoryEvent(event)

    @QtCore.Slot()
    def _raiseError(self):
        raise RuntimeError("this is a problem")

    @QtCore.Slot()
    def _showPreferencesForm(self):
        dialog = PreferencesDialog(self)  # shares taskbar entry and is centered on self
        dialog.exec_()
