
from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QDir, Signal, Slot, QSize, QSettings
from PySide2.QtWidgets import (
    QFileSystemModel, QListView, QWidget, QLabel,
    QHBoxLayout, QVBoxLayout, QToolButton, QAction,
    QSizePolicy, QPushButton, QFileDialog, QDialog,
    QScrollArea,
)

class Library(QWidget):

    def __init__(self, ctx):
        super().__init__()

        # context
        self.ctx = ctx

        # root path
        settings = QSettings()
        rootPath = settings.value(
            'library/homeDirectory',
            None
        )

        if rootPath is None:
            self.pathNotDefined()
        else:
            self.rebase(rootPath)

    def pathNotDefined(self):
        
        # prompt user to choose a flights folder
        button = QPushButton('Choose Flights Folder')
        button.clicked.connect(self.chooseRootFolder)

        # add to layout
        layout = QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

    def chooseRootFolder(self):

        # prompt user to choose folder
        dlg = QFileDialog()
        folder = dlg.getExistingDirectory(
            self,
            'Choose Flight Folder',
            Path().home().anchor,
            QFileDialog().ShowDirsOnly
        )

        if not folder == '':

            # remove old layout
            clearLayout(self.layout())

            # rebase view on new folder
            self.rebase(folder)

            # save this root path
            QSettings().setValue('library/homeDirectory', folder)

    def rebase(self, rootPath):

        # file model
        self.model = QFileSystemModel()
        self.model.setRootPath(rootPath)

        # file view
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(rootPath))

        # connection to update view window from view window interaction
        self.view.activated.connect(self.viewActivated)

        # address bar
        self.address = AddressBar(self.ctx)
        self.address.home_path = self.model.rootDirectory()
        self.address.path = self.model.rootDirectory()

        # connection to update view window based on address bar
        self.address.activated.connect(self.addressActivated)

        # layout init
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0,5,0,0)

        # add layout items
        self.layout().addWidget(self.address)
        self.layout().addWidget(self.view, stretch=1)

    def viewActivated(self, index):
        if self.model.fileInfo(index).isDir():
            self.view.setRootIndex(index)
            self.address.path = QDir(self.model.filePath(index))

    def addressActivated(self, path):
        index = self.model.index(path)
        self.viewActivated(index)


class AddressBar(QWidget):

    activated = Signal(str)

    def __init__(self, ctx):
        super().__init__()

        # context
        self.ctx = ctx

        # path defaults
        self._homePath = QDir.current()
        self._path = QDir.current()

        # layout
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

    @property
    def home_path(self):
        return self._homePath

    @home_path.setter
    def home_path(self, p):
        self._homePath = p
        self._update()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, p):
        self._path = p
        self._update()

    def emitHomePath(self):
        self.activated.emit(self.home_path.absolutePath())

    def emitArbitraryPath(self, p):
        self.activated.emit(p)

    def _update(self):

        # get relative file path
        rel = self.home_path.relativeFilePath(self.path.absolutePath())

        # clear the address bar
        layout = self.layout()
        clearLayout(layout)

        # init actions list
        actions = []

        # add home action
        act = QAction(
            QIcon(self.ctx.get_resource('home.png')),
            'Home',
        )
        act.triggered.connect(self.emitHomePath)
        actions.append(act)

        # home path
        home = Path(self.home_path.absolutePath())
        full = home

        # make actions for each path part
        for part in Path(rel).parts:
            act = QAction(part)
            full = full / part
            act.triggered.connect(
                lambda _=False, p=str(full): self.emitArbitraryPath(p)
            )
            actions.append(act)

        # combine actions with buttons and add to layout
        for a in actions:
            button = QToolButton()
            button.setDefaultAction(a)
            layout.addWidget(button)

def clearLayout(layout):
    while layout.count() > 0:
        item = layout.takeAt(0)
        if not item:
            continue

        w = item.widget()
        if w:
            w.deleteLater()
