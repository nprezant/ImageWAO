
import json

from PySide2 import QtWidgets, QtCore, QtGui

import scenegraphics as sg
from base.primatives import GrahphicItemRepresentation, CountData


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

    def __init__(self, reps: GrahphicItemRepresentation):
        '''
        Initialize class using one of the static methods:
        * loadItems, for loading scene items
        * loads, for loading via an encoded JSON string

        Item type, geometry, and pen color/width are tracked.
        '''

        # Internally store the graphical representation
        # of these scene objects. Contains nough information
        # to recreate from primitive objects
        self._reps:GrahphicItemRepresentation = reps

        # To iterate over these representations, we need an
        # iterater tracking variable
        self._index = 0

    @staticmethod
    def loadItems(items):
        '''
        Initialize with a list of QGraphicsItems.
        Supported items:
        QGraphicsRectItem
        QGrahpicsEllipseItem
        QGraphicsLineItem
        '''

        representations = []

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

            representations.append(GrahphicItemRepresentation(name, geom, pen))
        
        return JSONDrawnItems(representations)

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

            representations.append(GrahphicItemRepresentation(name, geom, pen))
        
        return JSONDrawnItems(representations)

    def dumps(self):
        '''
        Return the encoded drawing items as a JSON formatted string
        '''
        if len(self._reps) == 0:
            return None

        encoded = []
        for rep in self._reps:
            encoded.append([rep.name, rep.args, rep.penColor, rep.penWidth])

        return json.dumps(encoded)

    def addToScene(self, scene:QtWidgets.QGraphicsScene):
        '''
        Adds the internal geometries to a scene,
        returning the list of items
        '''
        items = []
        for rep in self._reps:
            if rep.name == 'Rect':
                item = sg.SceneCountDataRect.create(rep.geom, rep.pen)
            elif rep.name == 'Ellipse':
                item = sg.SceneCountDataEllipse.create(rep.geom, rep.pen)
            elif rep.name == 'Line':
                item = sg.SceneCountDataLine.create(rep.geom, rep.pen)
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
        for rep in self._reps:
            painter.setPen(rep.pen)
            rep.scale(sf)
            painter.setPen(rep.pen)
            if rep.name == 'Rect':
                painter.drawRect(rep.geom)
            elif rep.name == 'Ellipse':
                painter.drawEllipse(rep.geom)
            elif rep.name == 'Line':
                painter.drawLine(rep.geom)
        painter.end()

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index == len(self._reps):
            raise StopIteration
        data = self._reps[self._index]
        self._index += 1
        return data

