
from pathlib import Path

from PySide2.QtGui import QIcon
from PySide2.QtCore import Qt, QDir, Signal, Slot, QSize
from PySide2.QtWidgets import (
    QFileSystemModel, QListView, QWidget, QLabel,
    QHBoxLayout, QVBoxLayout, QToolButton, QAction,
    QSizePolicy, QFileDialog, QDialog,
    QScrollArea,
)

from tools import clearLayout


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
        act.setToolTip(f'Home: {self.home_path.absolutePath()}')
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