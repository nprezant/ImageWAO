from PySide2 import QtCore, QtGui

from drawingdata import DrawingDataList

from .enums import UserRoles


class PositionedIndexes:
    """
    Effectively a list of indexes in the proper positioned order.
    [[idx1 idx2]
     [idx3 idx4]
     [idx5 idx6]]
    """

    def __init__(self, indexes):
        """
        Creates a 2D list of of
        the indexes
        """

        # Instance variables
        self.relativeIndexes = []
        self.tops = []
        self.lefts = []

        # These are the absolute row and column position
        # numbers of the indexes as seen in the model
        absolutePositions = [(idx, idx.row(), idx.column()) for idx in indexes]

        # Need to sort such that we loop through by row.
        # Each column of the first row, then each of the second)
        # [(1,1), (1,2), (2,1), (2,2)]
        # To do this, we sort first by columns, then by rows.
        absolutePositions.sort(key=lambda x: (x[1], x[2]))

        # This way we know how many rows and columnss we have total
        uniqueAbsoluteRows = list(dict.fromkeys([x[1] for x in absolutePositions]))
        uniqueAbsoluteColumns = list(dict.fromkeys([x[2] for x in absolutePositions]))

        # These should be sorted, but it is not a guarantee in Python 3.6
        uniqueAbsoluteRows.sort()
        uniqueAbsoluteColumns.sort()

        # Generate a blank (None-filled) list of relative positions
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
        """
        Top and left of each index of the combined,
        relatively positioned data.

        The role must retreive a size-able object from the index
        (Must have .height() and .width() methods.)

        Returns the positions
        Return data: rowTops = [0, ..., ...,]
        Return data: columnTops = [0, ..., ...,]
        """

        # If we already computed this, no need to do it again
        if self.tops and self.lefts:
            return self.tops, self.lefts

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

        self.tops = rowTops
        self.lefts = columnLefts
        return rowTops, columnLefts

    def toImage(self, role):
        """
        Paints the internal relatively positioned items
        to an image, provided that the given role
        retreives an image from the index.
        """

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

    def indexAt(self, pos: QtCore.QPoint):
        """
        The index under a given point
        """

        # Safety check: these must be lists containing at least a [0]
        if not self.tops or self.lefts:
            self.resultantTopLefts(UserRoles.FullResImage)

        # If the point is in negative space, we don't
        # have any indexes that would use negative space
        if pos.x() < 0 or pos.y() < 0:
            return None

        # If we don't find the row or the column,
        # we cannot return an index
        rowFound = False
        colFound = False

        # Find the row that this point belongs to
        row = 0
        for y in self.tops[1:]:
            if pos.y() < y:
                rowFound = True
                continue
            row += 1

        # Find the column that this point belongs to
        col = 0
        for x in self.lefts[1:]:
            if pos.x() < x:
                colFound = True
                continue
            col += 1

        if rowFound and colFound:
            return self.relativeIndexes[row][col]
        else:
            return None

    def positionOfIndex(self, index):
        """
        Position of an index within the
        relativeIndexes 2D list.
        """
        for r, idxRow in enumerate(self.relativeIndexes):
            for c, idx in enumerate(idxRow):
                if index is idx:
                    return r, c

        return None

    def topOfIndex(self, idx):
        """
        Top integer value of this index
        """
        r, _ = self.positionOfIndex(idx)
        return self.tops[r]

    def leftOfIndex(self, idx):
        """
        Left integer value of this index
        """
        _, c = self.positionOfIndex(idx)
        return self.lefts[c]

    def positionData(self):
        """
        Generator for positional data
        of the relativeIndexes 2D list.
        returns (index, rowNumber, colNumber)
        """
        for r, idxRow in enumerate(self.relativeIndexes):
            for c, idx in enumerate(idxRow):
                yield idx, r, c


class MergedIndexes:
    """
    Class for merging the images at various
    indexes together.

    This class also includes helpful
    tools such as indexAt() which returns
    the index that a given QPoint is at.
    """

    def __init__(self, indexes: QtCore.QModelIndex):
        """
        Finds the selected images and, if there are any,
        generates a QImage of them stitched together.
        This image can be retreived through the resultantImage
        method.

        Returns None if nothing is selected.
        Assumes consistent sizes.
        (More precisely: assumes that all images are the
        same sie as the first image)
        """

        # Position the indexes relative to each other in a map
        # Note: 2D list cells with "None" had no index at that location
        self.positions = PositionedIndexes(indexes)

    def resultantImage(self):
        """
        The combined image generated from the set
        of indexes.
        """
        return self.positions.toImage(UserRoles.FullResImage)

    def setModelDrawings(self, model, items: DrawingDataList):
        """
        Set the drawings on the model, given the list
        of items currently drawn on the merged indexes.
        """

        # Assign each drawn item to it's index.
        assignments = self.assignDrawnItems(items)

        # For each index and drawing pairing, we need to set it on the
        # model. However, if the index is None, that means the drawing
        # was over a null space on the merged image.
        for idx, drawnItems in assignments.items():
            if idx is not None:
                model.setDrawings(idx, drawnItems)

    def assignDrawnItems(self, items: DrawingDataList):
        """
        Assign the items passed in to their proper
        corresponding index.
        """

        # Dict:
        # {index1: [rep1, rep2, rep3],
        # index2, [rep4, rep5, rep6]}
        assignments = {}

        # Determine which index each graphics object
        # belongs to. (Iterate through representations)
        for rep in items:

            idx = self.positions.indexAt(rep.center)
            idxTop = self.positions.topOfIndex(idx)
            idxLeft = self.positions.leftOfIndex(idx)

            # Offset this geometric representation
            # to be in the same coordinates as the index
            # that it is on top of.
            rep.offset(-idxLeft, -idxTop)

            # Add this pairing to the assignment list
            if idx in assignments.keys():
                assignments[idx].append(rep)
            else:
                assignments[idx] = [rep]

        # Each index must have a value assigned to it
        # by the end of this -- we can start out
        # by assigning each one to a blank list.
        stringAssignments = {}
        for idx, _, _, in self.positions.positionData():
            stringAssignments[idx] = None

        # For item in the, dump to a string
        for idx, reps in assignments.items():
            stringAssignments[idx] = DrawingDataList(reps)

        return stringAssignments

    def drawnItems(self) -> DrawingDataList:
        """
        Merge the drawn items for this combined image
        into one nice DrawingDataList.
        """

        # Tracks the graphical representations
        # of drawn items.
        reps = []

        for idx, r, c in self.positions.positionData():

            # If this is a null position, there is no data
            if idx is None:
                continue

            # Retreive the drawn item string
            items = idx.data(role=UserRoles.DrawnItems)

            # If there are no drawn items, go to the next
            # position.
            if items is None:
                continue

            # Find the top and left coordinates of this index
            top = self.positions.tops[r]
            left = self.positions.lefts[c]

            # Offset each item to it's proper location within
            # the merged image.
            for rep in items:
                rep.offset(left, top)
                reps.append(rep)

        # Return the whole set of drawn items
        return DrawingDataList(reps)
