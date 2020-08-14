from PySide2 import QtCore, QtWidgets

from .docktitlewidget import DockTitleWidget


class DockWidget(QtWidgets.QDockWidget):
    """
    This class implements the container for docking area widgets.
    """

    def __init__(self, title, icon, parent):
        """
        Initialize the dock widget.
        :type title: str
        :type icon: QIcon
        :type session: Session
        """
        super().__init__(title, parent, QtCore.Qt.Widget)
        self.setTitleBarWidget(DockTitleWidget(title, icon, self))
        self.topLevelChanged.connect(self._handleTopLevelChanged)

    def addTitleBarButton(self, button):
        """
        Add a button to the right side of the titlebar of this widget.
        :type button: T <= QPushButton|QToolButton
        """
        widget = self.titleBarWidget()
        widget.addButton(button)
        widget.updateLayout()

    def setTitleBarText(self, text: str):
        """
        Sets the text of the title bar.
        """
        if isinstance(self.titleBarWidget(), DockTitleWidget):
            self.titleBarWidget().titleLabel.setText(text)
        else:
            self.setWindowTitle(text)

    @QtCore.Slot(bool)
    def _handleTopLevelChanged(self, isFloating: bool):
        """
        Stores the title bar, lets the native window painter handle
        the look and feel of the floating widget. If we wanted to keep the
        custom widget as the title, could do something like this...

        isVisible = self.isVisible()
        if isFloating:
            # Setting window flags hides the widget
            self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.CustomizeWindowHint)
            if isVisible:
                self.show()
        """
        if isFloating:
            self._storedTitleBarWidget = self.titleBarWidget()
            self.setTitleBarWidget(None)
        else:
            self.setTitleBarWidget(self._storedTitleBarWidget)
