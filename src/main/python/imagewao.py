
from PySide2 import QtGui, QtCore, QtWidgets

from base import ctx
from importers import FlightImportWizard
from ui import DockWidget, TitleBarText, StatusBar, LoadingOverlay, Notifier, Library
from ui.messageboxes import DoYouWantToSave

from gridviewer import QImageGridView
from imageviewer import QImageEditor
from counttotals import CountTotals

QtCore.QCoreApplication.setOrganizationName('Namibia WAO')
QtCore.QCoreApplication.setOrganizationDomain('imagewao.com')
QtCore.QCoreApplication.setApplicationName('ImageWAO')

class QImageWAO(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Whether or not the application has changes
        self._dirty = False

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

        # Dock widgets are saved in a dictionary
        self._dockWidgets = {}

        # Dock widget creation
        # Access dock widgets like so: self._dockWidgets['Flight Explorer']
        self._addDockWidget(self.library, ctx.explorerIcon, 'Flight Explorer', startArea=QtCore.Qt.LeftDockWidgetArea)
        self._addDockWidget(self.grid, ctx.defaultDockIcon, 'Image Grids', startArea=QtCore.Qt.RightDockWidgetArea)
        self._addDockWidget(self.countTotals, ctx.defaultDockIcon, 'Count Totals', startArea=QtCore.Qt.LeftDockWidgetArea)

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
        self.library.fileActivated.connect(self.grid.selectFile)
        self.library.directoryChanged.connect(self.grid.addFolder)
        self.library.directoryChanged.connect(self.titleBarText.setFolderName)
        self.library.directoryChanged.connect(self.countTotals.readDirectory)

        # Image grid signal connections
        self.grid.loadProgress.connect(self.loadingOverlay.setProgress)
        self.grid.loadFinished.connect(self.loadingOverlay.fadeOut)
        self.grid.selectedImageChanged.connect(self.viewer.setImage)
        self.grid.selectedFilesChanged.connect(self.library.selectFiles)
        self.grid.notificationMessage.connect(self.notifier.notify)
        self.grid.statusMessage.connect(self.showStatusMessage)

        # Image viewer signal connections
        self.viewer.drawnItemsChanged.connect(self.grid.setDrawings)
        self.viewer.drawnItemsChanged.connect(self._markAsDirty)

        # Count totals form connections
        self.countTotals.fileActivated.connect(self.grid.selectFile)
        self.countTotals.selectedFilesChanged.connect(self.library.selectFiles)

        # File | Etc. Menus
        self._menusCreated = False
        self._makeMenus()

        # Toolbars
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.viewer.toolbar)

    @QtCore.Slot(tuple)
    def showStatusMessage(self, args):
        self.statusBar().showMessage(*args)

    def _addDockWidget(self, w, icon, name:str, startArea=QtCore.Qt.LeftDockWidgetArea):
        dock = DockWidget(name, icon, parent=self)
        dock.setWidget(w)
        self.addDockWidget(startArea, dock)
        self._dockWidgets[name] = dock

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

        a = QtWidgets.QAction('Save', self)
        a.setShortcut('Ctrl+S')
        a.triggered.connect(self._saveIfDirty)
        self.fileMenu.addAction(a)

        a = QtWidgets.QAction('Import Flight Images', self)
        a.triggered.connect(FlightImportWizard().openNew)
        self.fileMenu.addAction(a)

        a = QtWidgets.QAction('Notify test', self)
        a.setShortcut('Ctrl+n')
        a.triggered.connect(
            lambda:
            self.notifier.notify(''))
        self.fileMenu.addAction(a)

        a = QtWidgets.QAction('Reset settings', self)
        a.triggered.connect(
            lambda: QtCore.QSettings().clear())
        self.fileMenu.addAction(a)

    def _arrangeMenus(self):
        self.menuBar().addMenu(self.fileMenu)

    def _saveIfDirty(self):
        if self._dirty:
            self.save()

    def save(self):
        '''
        All save operations. Once saving is completed,
        The application will be marked clean.
        '''
        self.grid.save()
        self._markAsClean()

    def _markAsDirty(self, *args):
        '''
        Any signals that signify save-able changes were made
        should also connect to this slot, which will mark the 
        application as "dirty" such that the user will
        be prompted to save before exiting the application.
        '''
        self._dirty = True
        self.titleBarText.setDirty(True)

    def _markAsClean(self):
        '''
        This operation resets the _dirty flag and also updates the
        title bar to the clean state.
        '''
        self._dirty = False
        self.titleBarText.setDirty(False)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        '''
        Catch library change events and see if the application needs to save
        before accepting them.
        '''
        if obj == self.library:
            if event.type() == Library.Events.DirectoryChange:
                self._exitDirectoryEvent(event)

                # If we are going to change the directory, we'll need to clear
                # the images from the grid and from the viewer.
                if event.isAccepted():
                    self.grid.clear()
                    self.viewer.clear()

        return super().eventFilter(obj, event)

    def _exitDirectoryEvent(self, event: QtCore.QEvent):
        '''
        Ensures that changes are saved (or intentionally ignored)
        when a directory changes.
        '''
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

    def closeEvent(self, event:QtGui.QCloseEvent):
        '''
        Check to ensure that changes are saved if 
        the user wants to save them.
        '''
        self._exitDirectoryEvent(event)
