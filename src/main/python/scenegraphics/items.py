from PySide6 import QtWidgets, QtCore, QtGui

from .mixins import SceneCountsItemMixin


class SceneCountDataRect(SceneCountsItemMixin, QtWidgets.QGraphicsRectItem):
    """
    A scene rectangle item that can display animal count data on hover.
    Use the `create` method to generate the item with (geometry, pen) parameters.
    """

    @staticmethod
    def create(rect: QtCore.QRect, pen: QtGui.QPen):
        item = SceneCountDataRect(rect)
        item.setPen(pen)
        item.setAcceptHoverEvents(True)
        return item


class SceneCountDataEllipse(SceneCountsItemMixin, QtWidgets.QGraphicsEllipseItem):
    """
    A scene ellipse item that can display animal count data on hover.
    Use the `create` method to generate the item with (geometry, pen) parameters.
    """

    @staticmethod
    def create(rect: QtCore.QRect, pen: QtGui.QPen):
        item = SceneCountDataEllipse(rect)
        item.setPen(pen)
        item.setAcceptHoverEvents(True)
        return item


class SceneCountDataLine(SceneCountsItemMixin, QtWidgets.QGraphicsLineItem):
    """
    A scene line item that can display animal count data on hover.
    Use the `create` method to generate the item with (geometry, pen) parameters.
    """

    @staticmethod
    def create(line: QtCore.QLine, pen: QtGui.QPen):
        item = SceneCountDataLine(line)
        item.setPen(pen)
        item.setAcceptHoverEvents(True)
        return item
