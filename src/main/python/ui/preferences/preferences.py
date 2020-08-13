from PySide2 import QtWidgets, QtCore


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(
            self.windowFlags() & (~QtCore.Qt.WindowContextHelpButtonHint)
        )
