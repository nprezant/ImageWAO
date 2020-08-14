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
        self.titleBarWidget().titleLabel.setText(text)
