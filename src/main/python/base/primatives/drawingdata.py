
from PySide2 import QtCore


class DrawingData:

    def __init__(self, name, geom, pen):
        '''
        Minimum objects required to re-create an item
        drawn in a scene.

        Need name of item (Rect, Ellipse, Line)
        Need geometry of item (QRectF, QLine), 
        and the pen used to draw the item.
        '''
        self.name = name
        self.geom = geom
        self.pen = pen

    @property
    def args(self):
        '''
        Arguments necessary to recreate the graphical
        geometry.
        '''
        if self.name == 'Rect':
            rect = self.geom
            args = [rect.x(), rect.y(), rect.width(), rect.height()]

        elif self.name == 'Ellipse':
            rect = self.geom
            args = [rect.x(), rect.y(), rect.width(), rect.height()]

        elif self.name == 'Line':
            line = self.geom
            args = [line.x1(), line.y1(), line.x2(), line.y2()]

        return args

    @property
    def penColor(self):
        '''
        Pen color in #RRGGBB format
        '''
        return self.pen.color().name()

    @property
    def penWidth(self):
        '''
        Pen width as an integer
        '''
        return self.pen.width()

    @property
    def center(self):
        '''
        Center QPointF of the geometry
        '''
        return self.geom.center()

    def offset(self, x, y):
        '''
        Offset the geometry of this point by a given 
        x and y value.
        '''
        self.geom.translate(QtCore.QPointF(x, y))

    def scale(self, sf):
        '''
        Scales the geometry of this point by a
        scale factor.
        '''
        if self.name in ('Rect', 'Ellipse'):
            x = self.geom.x() * sf
            y = self.geom.y() * sf
            width = self.geom.width() * sf
            height = self.geom.height() * sf
            self.geom.setRect(x, y, width, height)

        elif self.name in 'Line':
            x1 = self.geom.x1() * sf
            y1 = self.geom.y1() * sf
            x2 = self.geom.x2() * sf
            y2 = self.geom.y2() * sf
            self.geom.setP1(QtCore.QPointF(x1, y1))
            self.geom.setP2(QtCore.QPointF(x2, y2))

        self.pen.setWidth(self.pen.width() * sf)
