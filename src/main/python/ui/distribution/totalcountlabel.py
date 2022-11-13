from PySide6 import QtWidgets, QtCore, QtGui


class TotalCountLabel(QtWidgets.QLabel):

    toolTipStyle = "QToolTip { color: black; }"
    baseWidgetStyle = "font-weight: bold;"

    def __init__(self, parent):
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(2)
        self.setMidLineWidth(2)

        self.setText("0")
        self.setToolTip("Total number of photos (distance to mean)")

        fm = self.fontMetrics()
        self.setFixedWidth(fm.width("##########"))
        self.setAlignment(QtCore.Qt.AlignCenter)

    def setBackgroundColor(self, color: QtGui.QColor):
        self._appendBaseStyleSheet(f"background-color: {color.name()}; color: white; ")

    def clearStyle(self):
        self._appendBaseStyleSheet("")
        pass

    def _appendBaseStyleSheet(self, additionalStyle: str):
        self.setStyleSheet(
            self.toolTipStyle
            + "TotalCountLabel { "
            + self.baseWidgetStyle
            + additionalStyle
            + "}"
        )
