from PySide6 import QtCore


class EventTypes:
    DirectoryChange = QtCore.QEvent.registerEventType()


class DirectoryChangeEvent(QtCore.QEvent):
    def __init__(self, proxyIndex, sourceIndex):
        super().__init__(QtCore.QEvent.User)
        self.proxyIndex = proxyIndex
        self.sourceIndex = sourceIndex

    def type(self):
        return EventTypes.DirectoryChange
