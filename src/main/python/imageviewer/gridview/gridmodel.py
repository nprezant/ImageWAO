
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

class ImageItem:
    def __init__(self, pixmap):
        self._pixmap = pixmap

class FullImage:

    def __init__(self, pixmap, rows=2, cols=2, scaledWidth=200):
        self._pixmap = pixmap
        self.rows = rows
        self.cols = cols
        self._scaledWidth = scaledWidth

        self.rects = []
        self.parts = []
        self.scaledParts = []

        self.compute()

    def part(self, r, c, scaled=True):
        ''' Returns a portions of this image.
        The portion is is computed as the item of the image at
        row r and column c, given that the image is divided
        into the class variable rows and cols.
        '''
        if scaled:
            return self.scaledParts[r][c]
        else:
            return self.parts[r][c]

    def compute(self):
        ''' Computes the rects of the image,
        divided into a grid self.rows by self.cols.
        Uses those rects to generate tables of the parts and scaled
        parts of this pixmap.
        '''
            
        self.rects = []
        self.parts = []
        self.scaledParts = []

        w = self._pixmap.width()
        h = self._pixmap.height()

        segmentWidth = w / self.cols
        segmentHeight = h / self.rows

        for row in range(self.rows):

            self.rects.append([])
            self.parts.append([])
            self.scaledParts.append([])

            for col in range(self.cols):

                x = w - (self.cols - col) * segmentWidth
                y = h - (self.rows - row) * segmentHeight

                rect = QtCore.QRect(x, y, segmentWidth, segmentHeight)

                self.rects[-1].append(rect)
                self.parts[-1].append(self._pixmap.copy(rect))
                self.scaledParts[-1].append(self.parts[-1][-1].scaledToWidth(self._scaledWidth))


class ImageDelegate(QtWidgets.QAbstractItemDelegate):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixelHeight = 200

    def paint(self, painter, option, index):
        if option.state == QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)

        if (option.state == QtWidgets.QStyle.State_Selected):
            painter.setBrush(option.palette.highlightedText())
        else:
            painter.setBrush(option.palette.text())

        painter.drawRect(
            QtCore.QRectF(
                option.rect.x(), option.rect.y(),
                option.rect.width(), option.rect.height()))
        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(self._pixelHeight, self._pixelHeight)

    def setPixelSize(self, size):
        self._pixelHeight = size
    
    
class QImageGridModel(QtCore.QAbstractTableModel):

    def __init__(self):
        super().__init__()

        self._imageRows = 2
        self._imageCols = 2
        self._displayWidth = 200

        self._images: FullImage = []

        # self._images = [
        #     FullImage(QtGui.QPixmap('C:/Flights/FlightXX/Transect02/Transect02_001.JPG'), self._imageRows, self._imageCols, self._displayWidth),
        #     FullImage(QtGui.QPixmap('C:/Flights/FlightXX/Transect02/Transect02_001.JPG'), self._imageRows, self._imageCols, self._displayWidth),
        #     FullImage(QtGui.QPixmap('C:/Flights/FlightXX/Transect02/Transect02_001.JPG'), self._imageRows, self._imageCols, self._displayWidth),
        # ]

    def tryAddFolder(self, path):

        searchFolder = Path(path)
        
        # list of relevant files
        imgFiles = []

        if not searchFolder.is_dir():
            return

        for filename in searchFolder.glob('*'):

            # rule out non-image files
            fp = Path(filename)
            if not fp.is_file():
                continue

            if not fp.suffix in ('.jpg', '.JPG', '.jpeg', '.JPEG'):
                continue

            imgFiles.append(fp)

        if len(imgFiles) == 0:
            return
        else:
            self.beginResetModel()
            self._images = []
            for fp in imgFiles:
                self.addImageFromPath(str(fp))
            self.endResetModel()

    def addImageFromPath(self, path):
        self._images.append(FullImage(
            QtGui.QPixmap(path), self._imageRows, self._imageCols, self._displayWidth))

    def rowCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        return len(self._images) * self._imageRows

    def columnCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of columns the model holds. '''
        return self._imageCols

    def data(self, index, role=QtCore.Qt.DecorationRole):
        ''' Depending on the index and role given, return data.
            If not returning data, return None (equv. to Qt's QVariant)
        '''
        if not index.isValid():
            return None

        if index.row() < 0:
            return None

        image = self._images[int(index.row() / self._imageRows)]

        r = index.row() % self._imageRows
        c = index.column()

        if role == QtCore.Qt.DecorationRole:
            return image.part(r, c)

        if role == QtCore.Qt.SizeHintRole:
            return image.part(r, c).size()

        if role == QtCore.Qt.UserRole:
            return image.part(r, c, False)

        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        ''' No headers are displayed.
        '''
        if (role == QtCore.Qt.SizeHintRole):
            return QtCore.QSize(1, 1)

        return None

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' Insert a row into the model. '''
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)

        for row in range(rows):
            pixmap = QtGui.QPixmap(20,20)
            pixmap.fill(QtGui.QColor(0,0,0)) # black
            self._images.insert(
                position + row,
                FullImage(pixmap)
            )

        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        ''' Remove a row into the model. '''
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)

        del self._images[position:position+rows]

        self.endRemoveRows()
        return True

    def flags(self, index):
        ''' Set the item flag at the given index. '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(
            QtCore.QAbstractTableModel.flags(self, index)
            # | QtCore.Qt.ItemIsEditable
        )
