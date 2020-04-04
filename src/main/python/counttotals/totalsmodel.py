
from PySide2 import QtCore, QtWidgets, QtGui

class TotalsModel(QtCore.QAbstractListModel):

    loadStarted = QtCore.Signal()
    loadProgress = QtCore.Signal(int)
    loadFinished = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self._data = [1,2,3,4]

        self._loadWorker = None
        self._threadpool = QtCore.QThreadPool()

    def rowCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        return len(self._data)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        '''
        Depending on the index and role given, return data.
        If not returning data, return None (equv. to Qt's QVariant)
        '''
        if not index.isValid():
            return None

        if index.row() < 0:
            return None

        if role == QtCore.Qt.DisplayRole:
            return self._data[index.row()]

        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        '''
        No headers are displayed.
        '''
        if (role == QtCore.Qt.SizeHintRole):
            return QtCore.QSize(1, 1)

        return None

    def flags(self, index):
        ''' Set the item flag at the given index. '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(
            QtCore.QAbstractListModel.flags(self, index)
            # | QtCore.Qt.ItemIsEditable
        )

