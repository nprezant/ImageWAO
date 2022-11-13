import json
from typing import List

from PySide6 import QtWidgets, QtGui

import scenegraphics as sg

from .drawingdata import DrawingData


class DrawingDataList:
    """
    Contains methods useful for encoding and
    decoding drawn items on a graphics scene.

    This class allows those items to be "offset"
    when the image they were drawn on is not necessarily
    the image that they should be saved on.

    This happens most commonly when imaged are
    "merged" before they are displayed in the viewer.
    """

    def __init__(self, drawings: List[DrawingData]):
        """
        The __init__ method loads drawing data directly.
        Other static methods are available to initialize the class:

        Can also initialize class using one of the static methods:
        * loadDrawingData, for loading drawing data items
        * loads, for loading via an encoded JSON string

        Item type, geometry, and pen color/width are tracked.
        """

        # Internally store the graphical representation
        # of these scene objects. Contains enough information
        # to recreate from primitive objects
        self._drawingData: List[DrawingData] = drawings

        # To iterate over this instance, we need an
        # iterater tracking variable
        self._index = 0

    @staticmethod
    def loadGraphicsItems(items: List[QtWidgets.QGraphicsItem]):
        """
        Initialize serializable data with a list of QGraphicsItems.
        Supported items:
        QGraphicsRectItem
        QGrahpicsEllipseItem
        QGraphicsLineItem
        """

        drawingData = []

        for item in items:

            # Encoded data differs depending on item type
            # Need to save as much data as necessary to re-create item
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                name = "Rect"
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
                name = "Ellipse"
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsLineItem):
                name = "Line"
                geom = item.line()

            else:
                raise TypeError(f"Unable to serialize item type: {type(item)}")

            # All graphics items have associated pens
            # All graphics items derived from the counts mixin have count data
            if isinstance(item, sg.SceneCountsItemMixin):
                pen = item.pen()
                countData = item.countData()
            else:
                raise TypeError(f"Unable to serialize item type: {type(item)}")

            drawingData.append(DrawingData(name, geom, pen, countData))

        return DrawingDataList(drawingData)

    @staticmethod
    def loads(s: str):
        """
        Load an encoded JSON formatted string list of drawing items
        as their geometric representation (QRectF, QLine, QEllipse)
        """

        if s is None:
            return DrawingDataList([])

        data = json.loads(s)

        return DrawingDataList.load(data)

    @staticmethod
    def load(data: List[dict]):
        """
        Loads JSON drawing data from a list of dicts
        """
        drawings = []
        for dataItem in data:

            drawing = DrawingData.fromDict(dataItem)

            if drawing is not None:
                drawings.append(drawing)

        return DrawingDataList(drawings)

    def dumps(self):
        """
        Return the encoded drawing items as a JSON formatted string
        """
        if len(self._drawingData) == 0:
            return None

        return json.dumps(self.toDict())

    def toDict(self):
        """
        Returns the encoded drawing items as a JSON serializable dict
        """
        encoded = []
        for drawing in self._drawingData:
            encoded.append(drawing.toDict())

        return encoded

    def addToScene(self, scene: QtWidgets.QGraphicsScene):
        """
        Adds the internal geometries to a scene,
        returning the list of items
        """
        items = []
        for drawing in self._drawingData:
            if drawing.name == "Rect":
                item = sg.SceneCountDataRect.create(drawing.geom, drawing.pen)
            elif drawing.name == "Ellipse":
                item = sg.SceneCountDataEllipse.create(drawing.geom, drawing.pen)
            elif drawing.name == "Line":
                item = sg.SceneCountDataLine.create(drawing.geom, drawing.pen)
            else:
                item = None

            if item is not None:
                item.setCountData(drawing.countData)
                scene.addItem(item)
                items.append(item)

        return items

    def paintToDevice(self, device, sf=1):
        """
        Paint the internal geometries to a
        paint device (QImage, QPixmap, etc.)

        Optionally include a scaling factor if
        you are painting to a different size than what
        the drawing was originally drawn on.
        """
        painter = QtGui.QPainter(device)
        for drawing in self._drawingData:
            drawing.scale(sf)
            painter.setPen(drawing.pen)
            if drawing.name == "Rect":
                painter.drawRect(drawing.geom)
            elif drawing.name == "Ellipse":
                painter.drawEllipse(drawing.geom)
            elif drawing.name == "Line":
                painter.drawLine(drawing.geom)
        painter.end()

    def isEmpty(self):
        return self._drawingData == []

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index == len(self._drawingData):
            raise StopIteration
        data = self._drawingData[self._index]
        self._index += 1
        return data
