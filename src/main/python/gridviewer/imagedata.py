
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from base import config
from serializers import JSONDrawnItems


class FullImage:
    '''
    Contains all image data necessary to draw in grid form or 
    as a full resolution image. Caches the gridded images so
    the computation only happens once.
    Provides convenient access to the images.
    '''

    def __init__(self, image, path=Path(), rows=2, cols=2, initialWidths=[200]):
        self.image = image
        self.path = path
        self.rows = rows
        self.cols = cols

        self.parts = []
        self.scaledParts = {}
        self._drawnItems = []

        self.breakUpImage()
        for w in initialWidths:
            self.computeScalings(w)

    def part(self, r, c, scaledWidth=None):
        '''
        Returns a portions of this image.
        The portion is is computed as the item of the image at
        row r and column c, given that the image is divided
        into the class variable rows and cols.

        If the scaledWidth is None, the full resolution image portion
        is returned.
        '''
        if scaledWidth is None:
            return self.parts[r][c]
        else:
            key = str(int(scaledWidth))
            try:
                return self.scaledParts[key][r][c]
            except KeyError:
                self.computeScalings(scaledWidth)
            finally:
                return self.scaledParts[key][r][c]

    def drawnPart(self, r, c, scaledWidth):
        '''
        Gets the scaled portion of this image,
        with the items drawn on it.
        '''
        img = self.part(r,c, scaledWidth).copy()

        # Add drawing items if present
        sItems = self.drawnItems(r,c)
        if sItems is not None:

            # Since we are drawing on a scaled part of the image,
            # we need to use the scale factor
            sf = scaledWidth / self.part(r,c,None).width()
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

    def computeScalings(self, width:int):
        '''
        Compute and populate the `scaldWidth` object
        '''
        width = int(width)
        
        scaledParts = []
        self.scaledParts[str(width)] = scaledParts

        for row in range(self.rows):
            scaledParts.append([])

            for col in range(self.cols):
                scaledParts[-1].append(self.parts[row][col].scaledToWidth(width))

    def breakUpImage(self):
        '''
        Computes the rects of the image,
        divided into a grid self.rows by self.cols.
        Uses those rects to generate tables of the
        parts of this pixmap.
        '''

        self.parts = []
        self._drawnItems = []

        w = self.image.width()
        h = self.image.height()

        segmentWidth = w / self.cols
        segmentHeight = h / self.rows

        for row in range(self.rows):

            self.parts.append([])
            self._drawnItems.append([])

            for col in range(self.cols):

                x = w - (self.cols - col) * segmentWidth
                y = h - (self.rows - row) * segmentHeight

                rect = QtCore.QRect(x, y, segmentWidth, segmentHeight)

                self.parts[-1].append(self.image.copy(rect))
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
