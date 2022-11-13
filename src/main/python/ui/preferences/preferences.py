from PySide6 import QtWidgets, QtCore

from base import config


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setWindowFlags(
            self.windowFlags() & (~QtCore.Qt.WindowContextHelpButtonHint)
        )

        usernameToolTip = "Username is exported to Excel along with animal counts"
        usernameLabel = QtWidgets.QLabel()
        usernameLabel.setText("Username")
        usernameLabel.setToolTip(usernameToolTip)
        self.usernameBox = QtWidgets.QLineEdit()
        self.usernameBox.setText(config.username)
        self.usernameBox.setPlaceholderText("Enter your name")
        self.usernameBox.setToolTip(usernameToolTip)

        form = QtWidgets.QFormLayout()
        form.addRow(usernameLabel, self.usernameBox)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.addButton(QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self._okPressed)
        buttonBox.rejected.connect(self.close)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    @QtCore.Slot()
    def _okPressed(self):
        config.username = self.usernameBox.text()
        self.close()
