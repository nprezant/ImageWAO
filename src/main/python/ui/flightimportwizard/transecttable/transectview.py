from PySide2 import QtGui, QtWidgets


class TransectTableView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Alternate row colors
        p = self.palette()
        p.setColor(p.AlternateBase, QtGui.QColor("#ffe8c9"))
        self.setPalette(p)
        self.setAlternatingRowColors(True)

        # Underline header text
        self.horizontalHeader().setStyleSheet(
            "QHeaderView { text-decoration: underline; }"
        )

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.matches(QtGui.QKeySequence.Paste):
            self._handlePaste()
        super().keyPressEvent(event)

    @property
    def clipboard(self):
        return QtWidgets.QApplication.instance().clipboard()

    def _handlePaste(self):
        clipboard_text = self.clipboard.text()
        rowContents = clipboard_text.strip("\n").split("\n")

        if len(self.selectedIndexes()) == 0:
            return

        initIndex = self.selectedIndexes()[0]
        initRow = initIndex.row()
        initCol = initIndex.column()

        for i in range(len(rowContents)):
            columnContents = rowContents[i].strip("\t").split("\t")
            for j in range(len(columnContents)):
                self.model().setData(
                    self.model().index(initRow + i, initCol + j), columnContents[j]
                )

    def sizeHint(self):
        return 1.25 * super().sizeHint()
