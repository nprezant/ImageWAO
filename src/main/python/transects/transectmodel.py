
import glob
import shutil
from pathlib import Path
from datetime import datetime

from PIL import Image

from PySide2 import QtGui, QtCore, QtWidgets

from base import config, QWorker


class Transect:

    def __init__(self, name='Transect', files=[]):
        self.name = name
        self.files = files

    @property
    def numFiles(self):
        return len(self.files)

    @property
    def firstLastText(self):
        first = self.files[0]
        last = self.files[-1]
        return f'{first.name} . . . {last.name}'

    def addFile(self, fp):
        self.files.append(fp)

    def clearFiles(self):
        self.files.clear()


class TransectTableModel(QtCore.QAbstractTableModel):

    copyProgress = QtCore.Signal(int)
    copyComplete = QtCore.Signal()

    categorizeProgress = QtCore.Signal(int)
    categorizeComplete = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.transects: Transect = []
        self.sections = ['Name', '# Images', 'Range']

        # For multithreaded copying and categorizing
        self._copyWorker = None
        self._categorizeWorker = None
        self._threadpool = QtCore.QThreadPool()

    def renameByOrder(self):
        for i,t in enumerate(self.transects):
            t.name = f'Transect{str(i).zfill(2)}'

    def readFolder(self, folder, maxDelay, minCount):
        '''
        Reads the image files from a given `folder` into the internal model.
        This process executes on a seperate thread. Use `categorizeProgess` and
        `categorizeComplete` to monitor progress.
        '''

        searchFolder = Path(folder)/'**'

        self._categorizeWorker = QWorker(categorizeFlightImages, [searchFolder, maxDelay, minCount])
        self._categorizeWorker.includeProgress()
        self._categorizeWorker.signals.progress.connect(self.categorizeProgress.emit)
        self._categorizeWorker.signals.finished.connect(self.categorizeComplete.emit)
        self._categorizeWorker.signals.result.connect(self.setTransects)
        self._threadpool.start(self._categorizeWorker)

    @QtCore.Slot(list)
    def setTransects(self, transects):
        self.beginResetModel()
        self.transects.clear()
        self.transects = transects
        self.endResetModel()

    def rowCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        return len(self.transects)

    def columnCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of columns the model holds. '''
        return len(self.sections)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        ''' Depending on the index and role given, return data.
            If not returning data, return None (equv. to Qt's QVariant)
        '''
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() > len(self.transects):
            return None

        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            name = self.transects[index.row()].name
            numFiles = self.transects[index.row()].numFiles
            fileRange = self.transects[index.row()].firstLastText

            if index.column() == 0:
                return name
            elif index.column() == 1:
                return numFiles
            elif index.column() == 2:
                return fileRange

        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        ''' Set the headers to be displayed. '''
        if role != QtCore.Qt.DisplayRole:
            return None

        if orientation == QtCore.Qt.Horizontal:
            return self.sections[section]

        if orientation == QtCore.Qt.Vertical:
            return section

        return None

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' Insert a row into the model. '''
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.transects.insert(
                position + row,
                Transect()
            )

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' Remove a row into the model. '''
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)

        del self.transects[position:position+rows]

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        '''
        Adjust the data (set it to <value>) depending on the
        given index and role.
        '''
        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.transects):
            transect = self.transects[index.row()]
            if index.column() == 0:
                transect.name = value
            else:
                return False

            self.dataChanged.emit(index, index)
            return True
        
        return False

    def flags(self, index):
        ''' Set the item flag at the given index. '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        if index.column() == 0:
            return QtCore.Qt.ItemFlags(
                QtCore.QAbstractTableModel.flags(self, index)
                | QtCore.Qt.ItemIsEditable)
        else:
            return QtCore.QAbstractTableModel.flags(self, index)

    def copyTransects(self, toFolder):
        '''
        Copys all internal transect files to another folder, `toFolder`
        on another thread. Use `copyProgress` and `copyComplete` to observe progress.
        '''
        self._copyWorker = QWorker(copyTransectFiles, [self.transects, toFolder])
        self._copyWorker.includeProgress()
        self._copyWorker.signals.progress.connect(self.copyProgress.emit) # bubble up progress
        self._copyWorker.signals.finished.connect(self.copyComplete.emit)
        self._threadpool.start(self._copyWorker)


def copyTransectFiles(transects, toFolder, progress=None):
    '''
    Copies all transect files to another folder
    If `progress` is passed in, emit progress along the way.
    '''

    # Ensure the base folder exists
    toFolder.mkdir(exist_ok=True)

    # Total number of files to copy
    numFiles = sum([t.numFiles for t in transects])
    numFilesCopied = 0

    for t in transects:

        # Make transect folder
        tFolder = toFolder / t.name
        tFolder.mkdir(exist_ok=True)

        for i, fp in enumerate(t.files):

            # Destination file name
            name = t.name + '_' + str(i).zfill(3) + fp.suffix
            dst = tFolder / name

            # Copy files
            shutil.copyfile(fp, dst)
            numFilesCopied += 1

            # If progress exists, emit it
            if progress is not None:
                progress.emit(int(numFilesCopied / numFiles * 100))

def categorizeFlightImages(searchFolder, maxDelay, minCount, progress=None):
    '''
    Categorizes the images in the searchFolder into transects
    based on `maxDelay` and `minCount`.
    
    glob.iglob is applied to str(searchFolder) to loop through image files.
    with the recursive flag set to true.
    '''
        
    lastdt = None
    transects = []
    currentTransect = Transect()

    # necessary because otherwise python references the last
    # transect used (odd behavior...?)
    currentTransect.clearFiles()

    # Find the total number of files to go through.
    numFiles = len([1 for f in glob.iglob(str(searchFolder), recursive=True)])

    for i,filename in enumerate(glob.iglob(str(searchFolder), recursive=True)):

        # If we have a progress indicater, use it
        if progress is not None:
            progress.emit(int(i/numFiles*100))

        # rule out non-image files
        fp = Path(filename)
        if not fp.is_file():
            continue

        if not fp.suffix in config.supportedImageExtensions:
            continue

        # retrieve date and time image was taken
        img = Image.open(fp)
        t = img._getexif()[36867]
        dt = datetime.strptime(t, '%Y:%m:%d %H:%M:%S')
        
        # add the file if this is the first one in a transect
        if lastdt is None:
            currentTransect.addFile(fp)

        else:

            # compute time delta between this image and the last one
            delta = (dt - lastdt).seconds

            # if the time is small, add to the current transect
            if delta <= maxDelay:
                currentTransect.addFile(fp)
                lastdt = dt

            # if the time is large, conclude this transect
            # and add the file to the next one
            else:
                
                # only record transect if it has enough images
                if currentTransect.numFiles >= minCount:
                    transects.append(currentTransect)
                
                # make a new transect instance
                currentTransect = Transect(files=[fp])
        
        # record time of this image
        lastdt = dt

    # record the last transect if it has enough images
    if currentTransect.numFiles >= minCount:
        transects.append(currentTransect)

    # If there is a progress bar, note that progress is 100%
    if progress is not None:
        progress.emit(100)

    return transects


if __name__ == '__main__':
    TransectTableModel().readFolder(r'C:/FlightsRaw/Flight2', 5 ,4)
