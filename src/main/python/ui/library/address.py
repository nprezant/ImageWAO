from pathlib import Path

from PySide6 import QtCore, QtWidgets

from tools import clearLayout
from base import ctx


class AddressBar(QtWidgets.QWidget):

    activated = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        # path defaults
        self._homePath = QtCore.QDir.current()
        self._path = QtCore.QDir.current()

        # layout
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
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

        # clear the address bar, re-add the home button
        layout = self.layout()
        clearLayout(layout)
        layout.addWidget(self._createHomeButton())

        # home path
        home = Path(self.home_path.absolutePath())
        full = home

        # Make list of buttons for each path part
        for part in Path(rel).parts:
            button = QtWidgets.QPushButton()
            button.setText(part + " /")
            button.setStyleSheet("text-align: left;")

            full = full / part

            button.clicked.connect(
                lambda _=False, p=str(full): self.emitArbitraryPath(p)
            )
            button.setMinimumWidth(1)
            layout.addWidget(button)

    def _createHomeButton(self) -> QtWidgets.QToolButton:
        button = QtWidgets.QPushButton()
        button.setIcon(ctx.icon("icons/home.png"))
        button.setToolTip(f"Home: {self.home_path.absolutePath()}")
        button.clicked.connect(self.emitHomePath)
        button.setStyleSheet(
            "padding-left: 5px;"
            "padding-right: 5px;"
            "padding-top: 2px;"
            "padding-bottom: 2px;"
        )
        button.setIconSize(QtCore.QSize(24, 24))
        return button
