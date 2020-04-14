
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from serializers import JSONDrawnItems
from transects import TransectSaveData
from base import QWorker, config
from tools import saveManyImages, roundToMultiple

from .merging import MergedIndexes
from .enums import UserRoles
from .imagedata import FullImage

    
class QImageGridModel(QtCore.QAbstractTableModel):

    loadProgress = QtCore.Signal(int)
    loadFinished = QtCore.Signal()
    message = QtCore.Signal(tuple)
    transectDataChanged = QtCore.Signal(TransectSaveData)

    def __init__(self):
        super().__init__()

        self._imageRows = 2
        self._imageCols = 2
        self._minimumImageWidth = 20
        self._singleImageWidth:int = None
        self._lastSingleImageWidth:int = None
        self._displayWidth:int = None
        self.setDisplayWidth(200)

        self._images: FullImage = []

        self._loadWorker = None
        self._threadpool = QtCore.QThreadPool()

        # Keep track of which indexes changed
        # so we know what to save
        self._changedIndexes = []

    def displayWidth(self):
        return self._displayWidth

    def setDisplayWidth(self, width):
        '''
        Sets the width of the viewport that these images
        will be displayed in. Use this to change the size
        that the images are rendered at.

        Internally, this updates the _singleImageWidth variable.
        '''
        self._displayWidth = width

        # Compute single image width
        numCols = self.columnCount()
        margin = config.gridImageMargin
        preciseImageWidth = self._displayWidth / numCols - (margin * (numCols+1))
        imageWidth = roundToMultiple(preciseImageWidth, config.gridImageUpdateWidth)

        # Only set this value if it is the same as the last once computed.
        # This fixes a bug that caused flip flopping image sizes and freezing
        # when the user hovers the mouse right on the verge
        # of a smaller/larger image width threshold.
        if imageWidth == self._lastSingleImageWidth:
            
            # Set the value if valid. Note that there is a minimum width
            if imageWidth < self._minimumImageWidth:
                self._singleImageWidth = self._minimumImageWidth
            else:
                self._singleImageWidth = imageWidth

        self._lastSingleImageWidth = imageWidth

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
        args=[imgList, self._imageRows, self._imageCols, [self._singleImageWidth]]
        self._loadWorker = QWorker(FullImage.CreateFromFiles, args)
        self._loadWorker.includeProgress()
        self._loadWorker.signals.progress.connect(self.loadProgress.emit) # bubble up progress
        self._loadWorker.signals.result.connect(self.resetImagesFromFullImages)
        self._loadWorker.signals.finished.connect(self.loadFinished.emit)
        self._threadpool.start(self._loadWorker)

    def _resetLoadWorker(self):
        '''
        The `_loadWorker` variable tracks the QWorker that is currently
        processing. Call this method when the QWorker finishes it's task
        to free it up for the next large load process.
        '''
        self._loadWorker = None

    def resetImagesFromFullImages(self, fullImages):
        self.beginResetModel()
        self._images = []
        self._images = fullImages
        self.endResetModel()
        self._readSaveData()

    def _readSaveData(self):
        '''
        Reads in save data, if it can be found.
        Save file specified in Config().
        '''

        # Nothing to read if there are no images
        if len(self._images) == 0:
            return
            
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

                # Since we just read in new data and will have changed
                # the indexes as a part of that, we should note that
                # these indexes actually don't have to be saved again.
                self._changedIndexes = []

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

    def transectData(self):
        ''' Computes the transect save data and returns it. '''
        if len(self._changedIndexes) == 0:
            return

        # If the save file doesn't exist, initialize empty.
        transectPath = self._folder() / Path(config.markedDataFile)
        if transectPath.exists():
            saveData = TransectSaveData.load(transectPath)
        else:
            saveData = TransectSaveData(fp=transectPath)

        # Only save files that have changed
        for index in self._changedIndexes:

            # If this index is None, i.e., was already taken care of
            # by a previous index (part of same overall image), continue 
            # to next index.
            if index is None:
                continue

            # Retreive the path of the original image, and find
            # the indexes of the images that also correspond
            # to that path.
            originalPath: Path = self.data(index, role=UserRoles.ImagePath)
            indexes = self.matchPath(originalPath)

            # Now that we have all the indexes associated with this
            # path, we no longer need them in "changedIndexes"
            for idx in indexes:
                try:
                    num = self._changedIndexes.index(idx)
                except ValueError:
                    pass
                else:
                    self._changedIndexes[num] = None

            # Merge the indexes togther, create a preview image
            mergedIndexes = MergedIndexes(indexes)
            _ = mergedIndexes.resultantImage()

            # Merge drawn items and draw them onto the image
            drawings = mergedIndexes.drawnItems()
            if drawings is not None:

                # We should only save these drawings if they aren't already saved.
                if not saveData.imageHasDrawings(originalPath.name, drawings):
                    saveData.addDrawings(originalPath.name, drawings)

            else:
                saveData.removeDrawings(originalPath.name)

        # Return the transect data
        return saveData

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

        if transectPath.exists():
            # Initialize save data from old data path
            saveData = TransectSaveData.load(transectPath)
        else:
            transectPath.touch()
            saveData = TransectSaveData(fp=transectPath)

        # List of images to be saved and the `save` arguments
        # [(image, ['C:/Photos/myFavoriteImage.jpg']), ]
        markedImages = []

        # Only save files that have changed
        for index in self._changedIndexes:

            # If this index is None, i.e., was already taken care of
            # by a previous index (part of same overall image), continue 
            # to next index.
            if index is None:
                continue

            # Retreive the path of the original image, and find
            # the indexes of the images that also correspond
            # to that path.
            originalPath: Path = self.data(index, role=UserRoles.ImagePath)
            indexes = self.matchPath(originalPath)

            # Now that we have all the indexes associated with this
            # path, we no longer need them in "changedIndexes"
            for idx in indexes:
                try:
                    num = self._changedIndexes.index(idx)
                except ValueError:
                    pass
                else:
                    self._changedIndexes[num] = None


            # Merge the indexes togther, create a preview image
            mergedIndexes = MergedIndexes(indexes)
            preview = mergedIndexes.resultantImage()

            # Form the new path (./.marked/Alpha_001.JPG)
            markedPath = markedFolder / originalPath.name

            # Merge drawn items and draw them onto the image
            drawings = mergedIndexes.drawnItems()
            if drawings is not None:

                # We should only save these drawings if they aren't
                # already saved.
                if not saveData.imageHasDrawings(originalPath.name, drawings):

                    # Add this image to the list of images
                    # to save and add the drawn item string to the save data
                    JSONDrawnItems.loads(drawings).paintToDevice(preview)
                    markedImages.append((preview, [str(markedPath)]))
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

        # Save & emit the transect data
        saveData.dump(transectPath)
        self.transectDataChanged.emit(saveData)

        # Clear the changed index list
        self._changedIndexes = []

        # On another thread, do the heavily-lifing of
        # saving the images.
        if len(markedImages) != 1:
            msg = f'Saving {len(markedImages) + 1} images...'
        else:
            msg = f'Saving {Path(*markedImages[0][1]).name}...'
        self.message.emit((msg,))
        self._saveWorker = QWorker(saveManyImages, [markedImages])
        self._saveWorker.signals.finished.connect(self._resetSaveWorker)
        self._saveWorker.signals.finished.connect(self._saveWorkerFinished)
        self._threadpool.start(self._saveWorker)

    def _saveWorkerFinished(self):
        self.message.emit(('Save complete', 5000))

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
            return image.drawnPart(r, c, self._singleImageWidth)

        if role == QtCore.Qt.SizeHintRole:
            return image.part(r, c, self._singleImageWidth).size()

        if role == UserRoles.FullResImage:
            return image.part(r, c, None)

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

    def inLastLocalRow(self, index):
        '''
        Returns `True` if the index is in the last row,
        relative to the image it is a part of.
        '''
        localRow = index.row() % self._imageRows # if 2x2, local row is 0 or 1
        if localRow == self._imageRows - 1:
            return True
        else:
            return False
