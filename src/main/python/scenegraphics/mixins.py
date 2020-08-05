"""
The custom drawings need to hold additional information
about the animal counts associated, and to be able to
display this information.
"""

from PySide2 import QtWidgets

from drawingdata import CountData


class SceneCountsItemMixin:
    """
    A QGraphicsScene mixin that can display count data
    when the `countData` property is set.

    This is not a full class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize drop shadow effect. Default to off.
        self._shadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        self.setGraphicsEffect(self._shadowEffect)
        self._shadowEffect.setEnabled(False)

    def setCountData(self, data: CountData):
        """
        Sets the count data to the provided data object.
        """
        self._countData = data

    def countData(self) -> CountData:
        """
        Returns the count data if it has been set.
        If nothing has been set, this will return the default count data.
        """
        try:
            return self._countData
        except AttributeError:
            self.setCountData(CountData())
            return CountData()

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        """
        Upon beginning to hover, the tool tip with animal counts will be
        displayed and the drop shadow effect will be enabled.
        """
        self.setToolTip(self.countData().toToolTip())

        self._shadowEffect.setEnabled(True)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        """
        When leaving the widget, the hover effects should be turned off.
        """
        self._shadowEffect.setEnabled(False)
