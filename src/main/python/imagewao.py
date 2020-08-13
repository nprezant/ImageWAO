from pathlib import Path

from PySide2 import QtGui, QtCore, QtWidgets

from base import ctx, config
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
        self.viewer = QImageEditor()
        self.setCentralWidget(self.viewer)

        # Dock widget references
        self.grid = QImageGridView()
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
            self.grid,
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
        self.library.fileActivated.connect(self.grid.selectFile)
        self.library.directoryChanged.connect(self.grid.addFolder)
        self.library.directoryChanged.connect(self.titleBarText.setFolderName)
        self.library.directoryChanged.connect(self.countTotals.readDirectory)
        self.library.showFlightInfoRequested.connect(self._showFlightInfoDock)
        self.library.showMigrationLogRequested.connect(self._showMigrationLogDock)

        # Image grid signal connections
        self.grid.loadProgress.connect(self.loadingOverlay.setProgress)
        self.grid.loadFinished.connect(self.loadingOverlay.fadeOut)
        self.grid.selectedImageChanged.connect(self.viewer.setImage)
        self.grid.selectedFilesChanged.connect(self.library.selectFiles)
        self.grid.notificationMessage.connect(self.notifier.notify)
        self.grid.statusMessage.connect(self.showStatusMessage)
        self.grid.countDataChanged.connect(self.countTotals.setTransectData)

        # Image viewer signal connections
        self.viewer.drawnItemsChanged.connect(self.grid.setDrawings)
        self.viewer.drawnItemsChanged.connect(self._markAsDirty)

        # Count totals form connections
        self.countTotals.fileActivated.connect(self.grid.selectFile)
        self.countTotals.selectedFilesChanged.connect(self.library.selectFiles)
        self.countTotals.requestDrawingUpdate.connect(
            self.grid.save
        )  # Hacky. Ideally you could request the data without saving.

        # Flight info form signals
        self.flightInfoForm.closeRequested.connect(self.flightInfoDock.hide)
        self.migrationLogForm.closeRequested.connect(self.migrationLogDock.hide)

        # File | Etc. Menus
        self._menusCreated = False
        self._makeMenus()

        # Toolbars
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.viewer.toolbar)

    @QtCore.Slot(tuple)
    def showStatusMessage(self, args):
        self.statusBar().showMessage(*args)

    @QtCore.Slot(str)
    def _showFlightInfoDock(self, flightFolder: str):
        fp = Path(flightFolder)
        self.flightInfoDock.setTitleBarText(f"Flight Info - {fp.name}")
        self.flightInfoDock.show()
        self.flightInfoForm.readFlightFolder(fp)

    @QtCore.Slot(str)
    def _showMigrationLogDock(self, transectFolder: str):
        fp = Path(transectFolder)
        self.migrationLogDock.setTitleBarText(
            f"Migration Log - {fp.parent.name}/{fp.name}"
        )
        self.migrationLogDock.show()
        self.migrationLogForm.readTransectFolder(fp)

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
        self.addDockWidget(startArea, dock)
        return dock

    def _makeMenus(self):
        self._createMenus()
        self._clearMenus()
        self._populateMenus()
        self._arrangeMenus()

    def _clearMenus(self):
        self.fileMenu.clear()
        self.infoMenu.clear()

    def _createMenus(self):
        if self._menusCreated is False:
            self.fileMenu = QtWidgets.QMenu("&File", self)
            self.expeMenu = QtWidgets.QMenu("&Exp.", self)  # Experimental
            self.infoMenu = QtWidgets.QMenu("&Info", self)
            self._menusCreated = True

    def _populateMenus(self):

        # File Menu
        a = QtWidgets.QAction("Save", self)
        a.setShortcut("Ctrl+S")
        a.triggered.connect(self._saveIfDirty)
        self.fileMenu.addAction(a)

        a = QtWidgets.QAction("Import Flight Images", self)
        a.triggered.connect(FlightImportWizard().openNew)
        self.fileMenu.addAction(a)

        self.fileMenu.addSeparator()

        a = QtWidgets.QAction("Preferences", self)
        a.triggered.connect(self._showPreferencesForm)
        self.fileMenu.addAction(a)

        # Experimental Menu
        a = QtWidgets.QAction("Test notification", self)
        a.setShortcut("Ctrl+N")
        a.triggered.connect(lambda: self.notifier.notify(""))
        self.expeMenu.addAction(a)

        a = QtWidgets.QAction("Reset settings", self)
        a.triggered.connect(lambda: QtCore.QSettings().clear())
        self.expeMenu.addAction(a)

        a = QtWidgets.QAction("Throw runtime error", self)
        a.triggered.connect(self._raiseError)
        self.expeMenu.addAction(a)

        # Info Menu
        self.infoMenu.addAction(QtWidgets.QAction(f"Version: {self.version}", self))

        # Create text box for user name
        widgetAction = QtWidgets.QWidgetAction(self.infoMenu)

        userNameWidget = QtWidgets.QWidget()
        userNameLayout = QtWidgets.QHBoxLayout()
        userNameLayout.setContentsMargins(0, 0, 0, 0)

        nameLabel = QtWidgets.QLabel("User")
        nameLabel.setToolTip("Username is exported to Excel along with animal counts")
        nameEdit = QtWidgets.QLineEdit(config.username)
        nameEdit.editingFinished.connect(
            lambda: setattr(config, "username", nameEdit.text())
        )
        nameEdit.setToolTip(nameLabel.toolTip())

        userNameLayout.addWidget(nameLabel)
        userNameLayout.addWidget(nameEdit)

        userNameWidget.setLayout(userNameLayout)
        widgetAction.setDefaultWidget(userNameWidget)

        self.infoMenu.addAction(widgetAction)

    def _arrangeMenus(self):
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.expeMenu)
        self.menuBar().addMenu(self.infoMenu)

    def _saveIfDirty(self):
        if self._dirty:
            self.save()

    def save(self):
        """
        All save operations. Once saving is completed,
        The application will be marked clean.
        """
        self.grid.save()
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
                    self.grid.clear()
                    self.viewer.clear()
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
