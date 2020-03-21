
import json

from PySide2 import QtWidgets, QtCore, QtGui

import scenegraphics as sg
from base.primatives import DrawingData, CountData


class JSONDrawnItems:
    '''
    Contains methods useful for encoding and
    decoding drawn items on a graphics scene.

    This class allows those items to be "offset"
    when the image they were drawn on is not necessarily
    the image that they should be saved on.

    This happens most commonly when imaged are
    "merged" before they are displayed in the viewer.
    '''

    def __init__(self, drawings: DrawingData):
        '''
        The __init__ method loads drawing data directly.
        Other static methods are available to initialize the class:

        Can also initialize class using one of the static methods:
        * loadDrawingData, for loading drawing data items
        * loads, for loading via an encoded JSON string

        Item type, geometry, and pen color/width are tracked.
        '''

        # Internally store the graphical representation
        # of these scene objects. Contains nough information
        # to recreate from primitive objects
        self._drawingData: DrawingData = drawings

        # To iterate over this instance, we need an
        # iterater tracking variable
        self._index = 0

    @staticmethod
    def loadDrawingData(items: QtWidgets.QGraphicsItem):
        '''
        Initialize serializable data with a list of QGraphicsItems.
        Supported items:
        QGraphicsRectItem
        QGrahpicsEllipseItem
        QGraphicsLineItem
        '''

        drawingData = []

        for item in items:

            # Encoded data differs depending on item type
            # Need to save as much data as necessary to re-create item
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                name = 'Rect'
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsEllipseItem):
                name = 'Ellipse'
                geom = item.rect()

            elif isinstance(item, QtWidgets.QGraphicsLineItem):
                name = 'Line'
                geom = item.line()

            else:
                print(f'Unrecognized item: {item}')
                continue

            # All graphics items have associated pens
            if isinstance(item, QtWidgets.QGraphicsItem):
                pen = item.pen()

            drawingData.append(DrawingData(name, geom, pen))
        
        return JSONDrawnItems(drawingData)

    @staticmethod
    def loads(s):
        '''
        Load an encoded JSON formatted string of drawing items
        as their geometric representation (QRectF, QLine, QEllipse)
        '''

        if s is None:
            return JSONDrawnItems([])
            
        representations = []
        data = json.loads(s)

        for dataItem in data:

            # TODO: Error checking -- enough data in list?
            # correct data in list?
            name = dataItem[0]
            args = dataItem[1]
            penColor = dataItem[2]
            penWidth = dataItem[3]

            # Setup pen
            pen = QtGui.QPen(penColor) # Does this color need to be a QColor?
            pen.setWidth(penWidth)

            if name == 'Rect':
                geom = QtCore.QRectF(*args)
            elif name == 'Ellipse':
                geom = QtCore.QRectF(*args)
            elif name == 'Line':
                geom = QtCore.QLineF(*args)

            representations.append(DrawingData(name, geom, pen))
        
        return JSONDrawnItems(representations)

    def dumps(self):
        '''
        Return the encoded drawing items as a JSON formatted string
        '''
        if len(self._drawingData) == 0:
            return None

        encoded = []
        for d in self._drawingData:
            encoded.append([d.name, d.args, d.penColor, d.penWidth])

        return json.dumps(encoded)

    def addToScene(self, scene:QtWidgets.QGraphicsScene):
        '''
        Adds the internal geometries to a scene,
        returning the list of items
        '''
        items = []
        for drawing in self._drawingData:
            if drawing.name == 'Rect':
                item = sg.SceneCountDataRect.create(drawing.geom, drawing.pen)
            elif drawing.name == 'Ellipse':
                item = sg.SceneCountDataEllipse.create(drawing.geom, drawing.pen)
            elif drawing.name == 'Line':
                item = sg.SceneCountDataLine.create(drawing.geom, drawing.pen)
            else:
                item = None

            if item is not None:
                scene.addItem(item)
                items.append(item)

        return items

    def paintToDevice(self, device, sf=1):
        '''
        Paint the internal geometries to a
        paint device (QImage, QPixmap, etc.)

        Optionally include a scaling factor if
        you are painting to a different size than what
        the drawing was originally drawn on.
        '''
        painter = QtGui.QPainter(device)
        for drawing in self._drawingData:
            painter.setPen(drawing.pen)
            drawing.scale(sf)
            painter.setPen(drawing.pen)
            if drawing.name == 'Rect':
                painter.drawRect(drawing.geom)
            elif drawing.name == 'Ellipse':
                painter.drawEllipse(drawing.geom)
            elif drawing.name == 'Line':
                painter.drawLine(drawing.geom)
        painter.end()

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index == len(self._drawingData):
            raise StopIteration
        data = self._drawingData[self._index]
        self._index += 1
        return data

