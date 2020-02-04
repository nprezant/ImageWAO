
import glob
from pathlib import Path
from datetime import datetime

from PIL import Image

from PySide2.QtGui import QKeyEvent, QKeySequence
from PySide2.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QItemSelectionModel, QRect
)
from PySide2.QtWidgets import QTableView, QApplication

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


class TransectTableModel(QAbstractTableModel):

    def __init__(self):
        super().__init__()

        self.transects: Transect = [
            Transect('T1', [1,2,3,4]),
            Transect('T2', [1,4]),
            Transect('T3', [1,2,3,4,5,6,7]),
        ]

        self.sections = ['Name', '# Images', 'Range']

    def renameByOrder(self):
        for i,t in enumerate(self.transects):
            t.name = f'Transect{str(i).zfill(2)}'

    def readFolder(self, folder, maxDelay, minCount):
        ''' Reads the files in a folder to construct the model '''

        searchFolder = Path(folder)/'**'
        self.transects.clear()
        lastdt = None
        currentTransect = Transect()

        # necessary because otherwise python references the last
        # transect used (odd behavior...?)
        currentTransect.clearFiles()

        for filename in glob.iglob(str(searchFolder), recursive=True):

            # rule out non-image files
            fp = Path(filename)
            if not fp.is_file():
                continue

            if not fp.suffix in ('.jpg', '.JPG', '.jpeg', '.JPEG'):
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
                        self.transects.append(currentTransect)
                    
                    # make a new transect instance
                    currentTransect = Transect(files=[fp])
            
            # record time of this image
            lastdt = dt

        # record the last transect if it has enough images
        if currentTransect.numFiles >= minCount:
            self.transects.append(currentTransect)

    def rowCount(self, index=QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        return len(self.transects)

    def columnCount(self, index=QModelIndex()):
        ''' Returns the number of columns the model holds. '''
        return len(self.sections)

    def data(self, index, role=Qt.DisplayRole):
        ''' Depending on the index and role given, return data.
            If not returning data, return None (equv. to Qt's QVariant)
        '''
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() > len(self.transects):
            return None

        if role == Qt.DisplayRole:
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

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        ''' Set the headers to be displayed. '''
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.sections[section]

        if orientation == Qt.Vertical:
            return section

        return None

    def insertRows(self, position, rows=1, index=QModelIndex()):
        ''' Insert a row into the model. '''
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            self.transects.insert(
                position + row,
                Transect()
            )

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        ''' Remove a row into the model. '''
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        del self.transects[position:position+rows]

        self.endRemoveRows()
        return True

    def setData(self, index, value, role=Qt.EditRole):
        ''' Adjust the data (set it to <value>) depending on the
            given index and role.
        '''
        if role != Qt.EditRole:
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
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
            QAbstractTableModel.flags(self, index)
            | Qt.ItemIsEditable
        )

class TransectTableView(QTableView):
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.Paste):
            self._handlePaste()

    @property
    def clipboard(self):
        return QApplication.instance().clipboard()

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


if __name__ == '__main__':
    TransectTableModel().readFolder(r'C:/FlightsRaw/Flight2', 5 ,4)
