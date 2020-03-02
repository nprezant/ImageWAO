
from PySide2 import QtGui, QtCore, QtWidgets

from base import ctx

from ui import DockWidget, TitleBarText

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

        # Whether or not the application has changes
        self._dirty = False

        # Title bar text is managed
        self.titleBarText = TitleBarText(ctx.app.applicationName())
        self.titleBarText.changed.connect(self.setWindowTitle)

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
        self._addDockWidget(self.grid, ctx.defaultDockIcon, 'Image Grids', startArea=QtCore.Qt.RightDockWidgetArea)
        self._addDockWidget(self.library, ctx.explorerIcon, 'Flight Explorer', startArea=QtCore.Qt.LeftDockWidgetArea)
        self._addDockWidget(self.animalAdder, ctx.defaultDockIcon, 'Animal Adder', startArea=QtCore.Qt.RightDockWidgetArea)
        self._addDockWidget(self.animalTotals, ctx.defaultDockIcon, 'Animal Totals', startArea=QtCore.Qt.RightDockWidgetArea)

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

        # Flight library signal connections
        self.library.fileActivated.connect(self._updateGridSelection)
        self.library.directoryChanged.connect(self._setGridImages)
        self.library.directoryChanged.connect(self.titleBarText.setFolderName)

        # Image grid signal connections
        self.grid.loadProgress.connect(self.progressBar.setValue)
        self.grid.selectedImageChanged.connect(self._updateViewerImage)
        self.grid.selectedFilesChanged.connect(self._updateLibraryFileSelection)
        self.grid.notificationMessage.connect(self._sendNotification)
        self.grid.drawnItemsChanged.connect(self.viewer.readSerializedDrawnItems)

        # Image viewer signal connections
        self.viewer.drawnItemsChanged.connect(self.grid.setDrawings)
        self.viewer.drawnItemsChanged.connect(self._markAsDirty)

        # File | Etc. Menus
        self._menusCreated = False
        self._makeMenus()

        # Toolbars
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.viewer.toolbar)

    @QtCore.Slot(list)
    def _updateLibraryFileSelection(self, files):
        self.library.selectFiles(files)

    @QtCore.Slot(str)
    def _setGridImages(self, path):
        self.grid.model().tryAddFolder(path)

    @QtCore.Slot(QtGui.QImage)
    def _updateViewerImage(self, image):
        self.viewer.setImage(image)

    @QtCore.Slot(str)
    def _updateGridSelection(self, path):
        self.grid.selectFile(path)

    @QtCore.Slot(str)
    def _sendNotification(self, msg):
        self.notifier.notify(msg)

    def _addDockWidget(self, w, icon, name:str, startArea=QtCore.Qt.LeftDockWidgetArea):
        dock = DockWidget(name, icon, parent=self)
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

        a = QtWidgets.QAction('Save', self)
        a.setShortcut('Ctrl+S')
        a.triggered.connect(self.save)
        self.fileMenu.addAction(a)

        a = QtWidgets.QAction('Import Flight Images', self)
        a.triggered.connect(self.importWizards.openNewFlight)
        self.fileMenu.addAction(a)

        action = QtWidgets.QAction('Notify test', self)
        action.setShortcut('Ctrl+n')
        action.triggered.connect(
            lambda:
            self.notifier.notify(''))
        self.fileMenu.addAction(action)

        a = QtWidgets.QAction('Reset settings', self)
        a.triggered.connect(
            lambda: QtCore.QSettings().clear())
        self.fileMenu.addAction(a)

    def _arrangeMenus(self):
        self.menuBar().addMenu(self.fileMenu)

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

    def closeEvent(self, event:QtGui.QCloseEvent):
        '''
        Check to ensure that changes are saved if 
        the user wants to save them.
        '''

        # If there are no changes,
        # simply accept the event.
        if not self._dirty:
            event.accept()
            return

        # Create message box
        box = QtWidgets.QMessageBox()
        box.setText('The transect has been modified.')
        box.setInformativeText('Do you want to save your changes?')
        box.setStandardButtons(
            QtWidgets.QMessageBox.Save
            | QtWidgets.QMessageBox.Discard
            | QtWidgets.QMessageBox.Cancel)
        box.setDefaultButton(QtWidgets.QMessageBox.Save)
        
        # Based on user response, either save, don't save,
        # or quit.
        ret = box.exec_()
        if ret == QtWidgets.QMessageBox.Save:
            self.save()
            event.accept()
        elif ret == QtWidgets.QMessageBox.Discard:
            event.accept()
        elif ret == QtWidgets.QMessageBox.Cancel:
            event.ignore()
        else:
            # Should never be reached
            event.ignore()
