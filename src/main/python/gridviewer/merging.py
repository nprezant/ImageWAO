
from PySide2 import QtCore, QtWidgets, QtGui

from .gridmodel import UserRoles


class PositionedIndexes:
    '''
    Effectively a list of indexes in the proper positioned order.
    [[idx1 idx2]
     [idx3 idx4]
     [idx5 idx6]]
    '''

    def __init__(self, indexes):
        '''
        Creates a 2D list of of 
        the indexes
        '''
        # These are the absolute row and column position
        # numbers of the indexes as seen in the model
        absolutePositions = [(idx, idx.row(), idx.column()) for idx in indexes]

        # Need to sort such that we loop through by row.
        # Each column of the first row, then each of the second)
        # [(1,1), (1,2), (2,1), (2,2)]
        # To do this, we sort first by columns, then by rows.
        absolutePositions.sort(key = lambda x: (x[1], x[2]))

        # This way we know how many rows and columnss we have total
        uniqueAbsoluteRows = list(dict.fromkeys([x[1] for x in absolutePositions]))
        uniqueAbsoluteColumns = list(dict.fromkeys([x[2] for x in absolutePositions]))

        # These should be sorted, but it is not a guarantee in Python 3.6
        uniqueAbsoluteRows.sort()
        uniqueAbsoluteColumns.sort()

        # Generate a blank (None-filled) list of relative positions
        self.relativeIndexes = []
        for _ in range(len(uniqueAbsoluteRows)):
            row = []
            for _ in range(len(uniqueAbsoluteColumns)):
                row.append(None)
            self.relativeIndexes.append(row)

        # For each row, column pair, we can place it
        # in a position relative to the others in the index list.
        for idx, r, c in absolutePositions:

            # By indexing the absolute row with the position in
            # the list of uniqueAbsoluteRows, we know which relative
            # row we need to place this in. Same for columns.
            relativeRow = uniqueAbsoluteRows.index(r)
            relativeColumn = uniqueAbsoluteColumns.index(c)

            self.relativeIndexes[relativeRow][relativeColumn] = idx

    def resultantTopLefts(self, role):
        '''
        Top and left of each index of the combined,
        relatively positioned data.

        The role must retreive a size-able object from the index
        (Must have .height() and .width() methods.)

        Returns the positions
        Return data: rowTops = [0, ..., ...,]
        Return data: columnTops = [0, ..., ...,]
        '''

        rowTops = [0]
        columnLefts = [0]
        columnWidthsPerRow = []

        for rowOfIndexes in self.relativeIndexes:

            # What is the maximum height of this row?
            maxRowHeight = 0

            # What are each of the column widths in this row?
            rowColumnWidths = []

            for idx in rowOfIndexes:

                # If the index is none, nothing is here
                if idx is None:
                    rowColumnWidths.append(0)
                    continue

                # Retreive the sizeable object from the data
                sizable = idx.data(role=role)

                # If this object has a greater height than anything
                # else in this row, that's great, we'll take it
                if sizable.height() > maxRowHeight:
                    maxRowHeight = sizable.height()

                # Keep track of the width of each column in
                # this row.
                rowColumnWidths.append(sizable.width())

            # The top of the next row will start at the top
            # of the last row + the height of the biggest
            # thing in the last row
            rowTops.append(rowTops[-1] + maxRowHeight)

            columnWidthsPerRow.append(rowColumnWidths)

        # Loop through each column in the dataset
        for c in range(len(columnWidthsPerRow[0])):

            # Get the widths of this column's items
            columnWidths = [row[c] for row in columnWidthsPerRow]

            # The left side of the next column will start at
            # the last column + the width of the largest
            # thing in this column
            maxWidth = max(columnWidths)
            columnLefts.append(columnLefts[-1] + maxWidth)

        return rowTops, columnLefts

    def toImage(self, role):
        '''
        Paints the internal relatively positioned items
        to an image, provided that the given role
        retreives an image from the index.
        '''

        tops, lefts = self.resultantTopLefts(role)

        width = max(lefts)
        height = max(tops)

        # Create a result QImage of appropriate size
        result = QtGui.QImage(QtCore.QSize(width, height), QtGui.QImage.Format_RGB32)

        # Construct painter for drawing image parts into the result
        painter = QtGui.QPainter(result)

        for y, indexRow in enumerate(self.relativeIndexes):
            for x, idx in enumerate(indexRow):

                # Sometimes images are skipped
                if idx is not None:
                    img = idx.data(role)
                    top = tops[y]
                    left = lefts[x]
                    painter.drawImage(left, top, img)

        painter.end()

        return result


class MergedIndexes:
    '''
    Class for merging the images at various
    indexes together.
    
    This class also includes helpful
    tools such as indexAt() which returns
    the index that a given QPoint is at.
    '''

    def __init__(self, indexes:QtCore.QModelIndex):
        '''
        Finds the selected images and, if there are any, 
        generates a QImage of them stitched together.
        This image can be retreived through the resultantImage
        method.
        
        Returns None if nothing is selected.
        Assumes consistent sizes.
        (More precisely: assumes that all images are the
        same sie as the first image)
        '''

        # Position the indexes relative to each other in a map
        # Note: 2D list cells with "None" had no index at that location
        self.positions = PositionedIndexes(indexes)

    def resultantImage(self):
        '''
        The combined image generated from the set
        of indexes.
        '''

        return self.positions.toImage(UserRoles.FullResImage)


    def indexAt(self, pos:QtCore.QPoint):
        pass
