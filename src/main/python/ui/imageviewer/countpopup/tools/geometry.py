from PySide6 import QtCore

from .clipping import cohenSutherlandClip


def nearestPosOnRect(pos: QtCore.QPoint, rect: QtCore.QRect):
    """
    Finds the position on a rectangle nearest to the given point.
    """

    # Bounds: xmax, ymax, xmin, ymin
    bounds = (rect.right(), rect.bottom(), rect.left(), rect.top())

    # Line origin point
    c = rect.center()

    # Clipped line: returns (x1, y1, x2, y2)
    clipped = cohenSutherlandClip(c.x(), c.y(), pos.x(), pos.y(), *bounds)

    # "clipped" should only be None if both points lie outside the
    # bounding area. This should never happen, since one point
    # is always the center of the area.
    assert clipped is not None

    # The nearest position to the given point, on the rectangle, is
    # the second point returned by the clipping function.
    _, _, x2, y2 = clipped
    return QtCore.QPoint(x2, y2)


def distanceToRect(pos: QtCore.QPoint, rect: QtCore.QRect):
    """
    Finds the distance from a given point to the rectangle.
    """

    # Intersection point on rectangle
    intersection = nearestPosOnRect(pos, rect)

    # Line from original point to intersection
    line = QtCore.QLineF(pos, intersection)
    return line.length()
