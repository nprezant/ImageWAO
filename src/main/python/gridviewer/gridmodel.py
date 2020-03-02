
from pathlib import Path
from multiprocessing import Queue

from PySide2 import QtCore, QtWidgets, QtGui

from serializers import JSONDrawnItems
from transects import TransectSaveData
from base import QWorker, config
from tools import saveManyImages

from .merging import MergedIndexes
from .enums import UserRoles


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

    def drawnPart(self, r, c):
        '''
        Gets the scaled portion of this image,
        with the items drawn on it.
        '''
        img = self.part(r,c).copy()

        # Add drawing items if present
        sItems = self.drawnItems(r,c)
        if sItems is not None:

            # Since we are drawing on a scaled part of the image,
            # we need to use the scale factor
            sf = self._scaledWidth / self.part(r,c,scaled=False).width()
            JSONDrawnItems.loads(sItems).paintToDevice(img, sf)
        
        return img

    def drawnItems(self, r, c):
        '''
        Gets the serialized string
        of the drawn items at the given 
        row, column
        '''
        return self._drawnItems[r][c]

    def setDrawings(self, r, c, drawings):
        '''
        Sets the serialized string of the 
        drawn items at the given row, column to
        the given value.
        '''
        self._drawnItems[r][c] = drawings

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
    def CreateFromFiles(files, *args, progress=None):

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
    message = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

        self._imageRows = 2
        self._imageCols = 2
        self._displayWidth = 200

        self._images: FullImage = []

        self._loadWorker = None
        self._threadpool = QtCore.QThreadPool()

        # Keep track of which indexes changed
        # so we know what to save
        self._changedIndexes = []

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

            if not fp.suffix in config.supportedImageExtensions:
                continue

            imgFiles.append(fp)

        if len(imgFiles) == 0:
            return
        else:
            self.resetImagesFromFiles(imgFiles)

    def resetImagesFromFiles(self, imgList):

        # Initialize runner with arguments for FullImage static constructor
        args=[imgList, self._imageRows, self._imageCols, self._displayWidth]
        self._loadWorker = QWorker(FullImage.CreateFromFiles, args)
        self._loadWorker.includeProgress()
        self._loadWorker.signals.progress.connect(self.progress.emit) # bubble up progress
        self._loadWorker.signals.result.connect(self.resetImagesFromFullImages)
        self._loadWorker.signals.finished.connect(self._resetLoadWorker)
        self._threadpool.start(self._loadWorker)

    def _resetLoadWorker(self):
        '''
        The `_loadWorker` variable tracks the QWorker that is currently
        processing. Call this method when the QWorker finishes it's task
        to free it up for the next large load process.
        '''
        print('resetting load worker')
        self._loadWorker = None

    def _resetProgress(self):
        # Reset progress bar after a brief time
        QtCore.QTimer.singleShot(1000, lambda: self.progress.emit(0))

    def resetImagesFromFullImages(self, fullImages):
        self.beginResetModel()
        self._images = []
        self._images = fullImages
        self.endResetModel()
        self._readSaveData()
        self._resetProgress()

    def _readSaveData(self):
        '''
        Reads in save data, if it can be found.
        Save file specified in Config().
        '''

        # Generate the save path
        originalFolder = self._folder()
        savePath = originalFolder / Path(config.markedDataFile)

        # If the path doesn't exist, don't try to load anything
        if not savePath.is_file():
            return
        
        # Load save data
        saveData = TransectSaveData.load(savePath)
        for imageName, drawings in saveData.drawings():
            
            # Merge indexes that compose this file, and
            # set the drawings to the merged set.
            indexes = self.matchPath(originalFolder / imageName)

            if not indexes:
                print(f'Warning: bad save file -- {imageName} not found.')
            else:
                mergedIndexes = MergedIndexes(indexes)
                mergedIndexes.setModelDrawings(self, drawings)

    def matchPath(self, path):
        matches = []
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                idx = self.index(r,c)
                if idx.data(UserRoles.ImagePath) == Path(path):
                    matches.append(idx)
        return matches

    def _folder(self, r=0, c=0):
        '''
        Retreives the folder of the image at index (r,c).
        '''
        return self.data(self.createIndex(r,c), UserRoles.ImagePath).parent

    @QtCore.Slot()
    def save(self):
        '''
        Save changes made to the images. This involves:
        * Writing drawing data to a file
        * Saving the marked up image to a file
        '''

        if len(self._changedIndexes) == 0:
            return

        # Setup save directory files and folders
        markedFolder = self._folder() / Path(config.markedImageFolder)
        markedFolder.mkdir(exist_ok=True)

        transectPath = self._folder() / Path(config.markedDataFile)
        transectPath.parent.mkdir(exist_ok=True)
        transectPath.touch()

        # Initialize save data from old data path
        saveData = TransectSaveData.load(transectPath)

        # List of images to be saved and the `save` arguments
        # [(image, ['C:/Photos/myFavoriteImage.jpg']), ]
        markedImages = []

        # Only save files that have changed
        for index in self._changedIndexes:

            # Retreive the path of the original image, and find
            # the indexes of the images that also correspond
            # to that path.
            originalPath: Path = self.data(index, role=UserRoles.ImagePath)
            indexes = self.matchPath(originalPath)

            # Now that we have all the indexes associated with this
            # path, we no longer need them in "changedIndexes"
            for idx in indexes:
                try:
                    self._changedIndexes.remove(idx)
                except ValueError:
                    pass

            # Merge the indexes togther, create a preview image
            mergedIndexes = MergedIndexes(indexes)
            preview = mergedIndexes.resultantImage()

            # Form the new path (./.marked/Alpha_001.JPG)
            markedPath = markedFolder / originalPath.name

            # Merge drawn items and draw them onto the image
            drawings = mergedIndexes.drawnItems()
            if drawings is not None:
                JSONDrawnItems.loads(drawings).paintToDevice(preview)

                # Add this to the list of images to save
                markedImages.append((preview, [str(markedPath)]))

                # Add drawing items to the save data for this image
                saveData.addDrawings(originalPath.name, drawings)

            # If there are no drawings, we should delete the image
            # from the marked folder. (If applicable.)
            else:
                try:
                    markedPath.unlink()
                except FileNotFoundError:
                    pass
                finally:
                    # Ensure that there are no drawings saved alongside
                    # this image (in particular, if the drawings already
                    # existed, we need to delete them)
                    saveData.removeDrawings(originalPath.name)

        # Save the transect data
        saveData.dump(transectPath)

        # Clear the changed index list
        self._changedIndexes = []

        # On another thread, do the heavily-lifing of
        # saving the images.
        self.message.emit(
            f'Saving {len(markedImages)} images.\n\n'
            'Please do not exit the application :)'
        )
        self._saveWorker = QWorker(saveManyImages, [markedImages])
        self._saveWorker.signals.finished.connect(self._resetSaveWorker)
        self._saveWorker.signals.finished.connect(self._saveWorkerFinished)
        self._threadpool.start(self._saveWorker)

    def _saveWorkerFinished(self):
        self.message.emit('Save complete')

    def _resetSaveWorker(self):
        self._saveWorker = None

    def setDrawings(self, index, drawings):
        ''' Sets the drawn items at this index '''
        image = self._images[int(index.row() / self._imageRows)]
        
        r = index.row() % self._imageRows
        c = index.column()

        image.setDrawings(r, c, drawings)

        # Mark this index as "changed"
        self._changedIndexes.append(index)

        # Note that the data for this index changed
        # so the view can update accordingly
        self.dataChanged.emit(index, index, [QtCore.Qt.DecorationRole])

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
            return image.drawnPart(r, c)

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
