
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from transects import TransectSaveData
from base import QWorker, config
from base.primatives import CountDataSet

from .enums import UserRoles


class TotalsModel(QtCore.QAbstractListModel):

    loadStarted = QtCore.Signal()
    loadProgress = QtCore.Signal(int)
    loadFinished = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self._data = CountDataSet()
        self._parentDir = None

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
            return self._data.displayIndex(index.row())

        if role == UserRoles.AbsolutePath:
            return str(Path(self._parentDir) / list(self._data.keys())[index.row()])

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

    def readDirectory(self, fp):
        ''' Populates model from directory. `fp`: any Path()-able type'''
        self._parentDir = str(fp)
        fp = Path(fp)

        # Error checks
        if not fp.exists():
            raise ValueError(f'Cannot read data from path that does not exist: {fp}')
        if not fp.is_dir():
            raise ValueError(f'Can only read from dir, not file: {fp}')
        
        # If the .marked/ folder exists, this is a single transect
        markedFolder = fp / config.markedImageFolder
        if markedFolder.exists():

            # If the save file exists, read it
            saveFile = fp / config.markedDataFile
            if saveFile.exists():
                saveData = TransectSaveData.load(saveFile)
                dataSet = saveData.countDataSet()
                self._resetData(dataSet)
            else:
                return # No data saved to this transect yet

    def _resetData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()


