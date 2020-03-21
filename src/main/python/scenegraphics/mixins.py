'''
The custom drawings need to hold additional information
about the animal counts associated, and to be able to
display this information.
'''

from PySide2 import QtGui, QtCore, QtWidgets

class SceneCountsItemMixin:
    '''
    A QGraphicsScene mixin that can display count data
    when the `countData` property is set.

    This is not a full class.
    '''

    def hoverEnterEvent(self, event:QtWidgets.QGraphicsSceneHoverEvent):
        self.setToolTip('1 Ostrich')

    def hoverLeaveEvent(self, event:QtWidgets.QGraphicsSceneHoverEvent):
        print('leave event -- got to hide that "..." widget now')
