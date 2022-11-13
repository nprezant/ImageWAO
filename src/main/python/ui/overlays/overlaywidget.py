from PySide6 import QtWidgets, QtCore


class OverlayWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.newParent()

    def newParent(self):
        if not self.parent():
            return
        self.parent().installEventFilter(self)
        self.resize(self.parent().size())
        self.raise_()

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent):
        """
        Catches resize and child events from the parent widget.
        """
        if obj == self.parent():
            if event.type() == QtCore.QEvent.Resize:
                self.resize(self.parent().size())
            elif event.type() == QtCore.QEvent.ChildAdded:
                self.raise_()
        return super().eventFilter(obj, event)

    def event(self, event: QtCore.QEvent):
        """
        Tracks when the parent widget changes.
        """
        if event.type() == QtCore.QEvent.ParentAboutToChange:
            if self.parent():
                self.parent().removeEventFilter(self)
            elif event.type() == QtCore.QEvent.ParentChange:
                self.newParent()
        return super().event(event)
