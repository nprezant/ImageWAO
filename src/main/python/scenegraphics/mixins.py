'''
The custom drawings need to hold additional information
about the animal counts associated, and to be able to
display this information.
'''

from PySide2 import QtGui, QtCore, QtWidgets

from base.primatives import CountData


class SceneCountsItemMixin:
    '''
    A QGraphicsScene mixin that can display count data
    when the `countData` property is set.

    This is not a full class.
    '''

    def setCountData(self, data:CountData):
        '''
        Sets the count data to the provided data object.
        '''
        self._countData = data

    def countData(self) -> CountData:
        '''
        Returns the count data if it has been set.
        Otherwise, this return None.
        '''
        try:
            return self._countData
        except AttributeError:
            return None

    def hoverEnterEvent(self, event:QtWidgets.QGraphicsSceneHoverEvent):
        if isinstance(self.countData(), CountData):
            tip = self.countData().toToolTip()
        else:
            tip = None
        self.setToolTip(tip)

    def hoverLeaveEvent(self, event:QtWidgets.QGraphicsSceneHoverEvent):
        print('leave event -- got to hide that "..." widget now')
