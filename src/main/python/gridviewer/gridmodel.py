
from pathlib import Path
from multiprocessing import Queue

from PySide2 import QtCore, QtWidgets, QtGui

from base import QWorker

class UserRoles:
    FullResImage = QtCore.Qt.UserRole # No scaling involved
    EntireImage = QtCore.Qt.UserRole + 1 # Entire image (not cropped into sections)
    ImagePath = QtCore.Qt.UserRole + 2 # Path to the original image
    DrawnItems = QtCore.Qt.UserRole + 3 # Items drawn on this image

class FullImage:

    def __init__(self, image, path=Path(), rows=2, cols=2, scaledWidth=200):
        self.image = image
        self.path = path
        self.rows = rows
        self.cols = cols
        self._scaledWidth = scaledWidth

        self.rects = []
        self.parts = []
        self.scaledParts = []
        self._drawnItems = []

        self.compute()

    def part(self, r, c, scaled=True):
        '''
        Returns a portions of this image.
        The portion is is computed as the item of the image at
        row r and column c, given that the image is divided
        into the class variable rows and cols.
        '''
        if scaled:
            return self.scaledParts[r][c]
        else:
            return self.parts[r][c]

    def drawnItems(self, r, c):
        '''
        Gets the serialized string
        of the drawn items at the given 
        row, column
        '''
        return self._drawnItems[r][c]

    def setDrawnItems(self, r, c, items):
        '''
        Sets the serialized string of the 
        drawn items at the given row, column to
        the given value.
        '''
        self._drawnItems[r][c] = items

    def compute(self):
        '''
        Computes the rects of the image,
        divided into a grid self.rows by self.cols.
        Uses those rects to generate tables of the parts and scaled
        parts of this pixmap.
        '''
            
        self.rects = []
        self.parts = []
        self.scaledParts = []
        self._drawnItems = []

        w = self.image.width()
        h = self.image.height()

        segmentWidth = w / self.cols
        segmentHeight = h / self.rows

        for row in range(self.rows):

            self.rects.append([])
            self.parts.append([])
            self.scaledParts.append([])
            self._drawnItems.append([])

            for col in range(self.cols):

                x = w - (self.cols - col) * segmentWidth
                y = h - (self.rows - row) * segmentHeight

                rect = QtCore.QRect(x, y, segmentWidth, segmentHeight)

                self.rects[-1].append(rect)
                self.parts[-1].append(self.image.copy(rect))
                self.scaledParts[-1].append(self.parts[-1][-1].scaledToWidth(self._scaledWidth))
                self._drawnItems[-1].append(None)

    @staticmethod
    def CreateFromListQWorker(files, *args, progress=None):

        images = []
        count = len(files)

        for i, fp in enumerate(files):
            if not progress is None:
                progress.emit(int((i / count)*100))
            images.append(FullImage(QtGui.QImage(str(fp)), Path(fp), *args))
        
        if not progress is None:
            progress.emit(100)

        return images


# class ImageDelegate(QtWidgets.QAbstractItemDelegate):

#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._pixelHeight = 200

#     def paint(self, painter, option, index):
#         if option.state == QtWidgets.QStyle.State_Selected:
#             painter.fillRect(option.rect, option.palette.highlight())

#         painter.save()
#         painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
#         painter.setPen(QtCore.Qt.NoPen)

#         if (option.state == QtWidgets.QStyle.State_Selected):
#             painter.setBrush(option.palette.highlightedText())
#         else:
#             painter.setBrush(option.palette.text())

#         painter.drawRect(
#             QtCore.QRectF(
#                 option.rect.x(), option.rect.y(),
#                 option.rect.width(), option.rect.height()))
#         painter.restore()

#     def sizeHint(self, option, index):
#         return QtCore.QSize(self._pixelHeight, self._pixelHeight)

#     def setPixelSize(self, size):
#         self._pixelHeight = size
    
    
class QImageGridModel(QtCore.QAbstractTableModel):

    progress = QtCore.Signal(int)

    def __init__(self):
        super().__init__()

        self._imageRows = 2
        self._imageCols = 2
        self._displayWidth = 200

        self._images: FullImage = []

        self._runner = None
        self._threadpool = QtCore.QThreadPool()

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
            self.resetImagesFromList(imgFiles)

    
    def resetImagesFromList(self, imgList):

        self._runner = QWorker(
            FullImage.CreateFromListQWorker,
            args=[
                imgList, self._imageRows,
                self._imageCols, self._displayWidth], # Arguments for the CreateFromListQWorker function
            progress=True,
        )

        self._runner.signals.progress.connect(self.progress.emit) # bubble up progress
        self._runner.signals.result.connect(self.resetImagesFromFullImages)
        self._threadpool.start(self._runner)

    def _resetProgress(self):
        # Reset progress bar after a brief time
        QtCore.QTimer.singleShot(1000, lambda: self.progress.emit(0))

    def resetImagesFromFullImages(self, fullImages):
        self.beginResetModel()
        self._images = []
        self._images = fullImages
        self.endResetModel()
        self._resetProgress()

    def matchPath(self, path):
        matches = []
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                idx = self.index(r,c)
                if idx.data(UserRoles.ImagePath) == Path(path):
                    matches.append(idx)
        return matches

    @staticmethod
    def mergeIndexes(indexes):
        '''
        Finds the selected images and, if there are any, 
        returns a QImage of them stitched together. Returns
        None if nothing is selected.
        Assumes consistent sizes.
        '''

        # Nothing to do if nothing is selected
        if len(indexes) == 0:
            return None

        # Get the full resolution image parts (QImage, row, col)
        imageData = [
            (idx.data(role=UserRoles.FullResImage), idx.row(), idx.column()) for idx in indexes
        ]
        
        # Determine merged image size.
        # Keep track of unique rows and columns.
        # Keep track of total merged width and total merged height
        rows = []
        cols = []
        w = 0
        h = 0
        for img, r, c in imageData:

            if not r in rows:
                rows.append(r)
                h += img.height()

            if not c in cols:
                cols.append(c)
                w += img.width()

        # Create a result QImage of appropriate size
        result = QtGui.QImage(QtCore.QSize(w, h), QtGui.QImage.Format_RGB32)

        # Construct painter for drawing image parts into the result
        painter = QtGui.QPainter(result)

        # Sort the rows and columns to be in numerical order (1, 3, 4)
        rows.sort()
        cols.sort()

        # Paint the images into the result
        for img, r, c in imageData:

            # How far down in the list of rows/cols are we, relative to the rows/cols selected?
            rowNum = rows.index(r)
            colNum = cols.index(c)

            # The x,y position of this image is the (image width) * (the row or column)
            x = colNum * img.width()
            y = rowNum * img.height()

            # Draw
            painter.drawImage(x, y, img)

        return result

    def setDrawnItems(self, index, items):
        ''' Sets the drawn items at this index '''
        image = self._images[int(index.row() / self._imageRows)]
        
        r = index.row() % self._imageRows
        c = index.column()

        image.setDrawnItems(r, c, items)

    def rowCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of rows the model holds. '''
        return len(self._images) * self._imageRows

    def columnCount(self, index=QtCore.QModelIndex()):
        ''' Returns the number of columns the model holds. '''
        return self._imageCols

    def data(self, index, role=QtCore.Qt.DecorationRole):
        '''
        Depending on the index and role given, return data.
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

        if role == UserRoles.FullResImage:
            return image.part(r, c, False)

        if role == UserRoles.EntireImage:
            return image.image

        if role == UserRoles.ImagePath:
            return image.path

        if role == UserRoles.DrawnItems:
            return image.drawnItems(r, c)

        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        '''
        No headers are displayed.
        '''
        if (role == QtCore.Qt.SizeHintRole):
            return QtCore.QSize(1, 1)

        return None

    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        '''
        Insert a row into the model.
        '''
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
