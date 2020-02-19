
from PySide2 import QtGui, QtWidgets

class TransectTableView(QtWidgets.QTableView):
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.matches(QtGui.QKeySequence.Paste):
            self._handlePaste()
        super().keyPressEvent(event)

    @property
    def clipboard(self):
        return QtWidgets.QApplication.instance().clipboard()

    def _handlePaste(self):
        clipboard_text = self.clipboard.text()
        rowContents = clipboard_text.strip('\n').split('\n')

        if len(self.selectedIndexes()) == 0:
            return

        initIndex = self.selectedIndexes()[0]
        initRow = initIndex.row()
        initCol = initIndex.column()

        for i in range(len(rowContents)):
            columnContents = rowContents[i].strip('\t').split('\t')
            for j in range(len(columnContents)):
                self.model().setData(
                    self.model().index(
                        initRow + i,
                        initCol + j
                    ), 
                    columnContents[j]
                )
