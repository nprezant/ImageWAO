from PySide2 import QtCore, QtGui, QtWidgets

from base import ctx


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


class DockTitleWidget(QtWidgets.QWidget):
    """
    This class implements the title area of docking area widgets.
    """

    def __init__(self, title, icon, parent=None):
        """
        Initialize the widget.
        :type title: str
        :type icon: QIcon
        :type parent: QDockWidget
        """
        super().__init__(parent)
        # CREATE TITLEBAR ICON AND TITLE
        self.imageLabel = QtWidgets.QLabel(self)
        self.imageLabel.setPixmap(icon.pixmap(18))
        self.imageLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.imageLabel.setContentsMargins(0, 0, 0, 0)
        self.imageLabel.setFixedSize(18, 18)
        self.titleLabel = QtWidgets.QLabel(title, self)
        self.titleLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.titleLabel.setContentsMargins(4, 0, 0, 0)
        # self.titleLabel.setFont(Font('Roboto', 13))
        # CREATE STANDARD BUTTONS
        close = QtWidgets.QPushButton(self)
        close.setIcon(ctx.closeDockIcon)
        # close.setText('x')
        close.setFixedSize(18, 18)
        close.clicked.connect(parent.close)
        self.buttons = [close]
        # CONFIGURE LAYOUT
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setContentsMargins(6, 4, 6, 4)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        # self.setFont(Font('Roboto', 13))
        self.updateLayout()

    #############################################
    #   INTERFACE
    #################################

    def addButton(self, button):
        """
        Add a button to the right side of the titlebar, before the close button.
        :type button: T <= QPushButton|QToolButton
        """
        self.buttons.insert(0, button)

    def updateLayout(self):
        """
        Redraw the widget by updating its layout.
        """
        # CLEAR CURRENTY LAYOUT
        for i in reversed(range(self.mainLayout.count())):
            item = self.mainLayout.itemAt(i)
            self.mainLayout.removeItem(item)
        # DISPOSE NEW ELEMENTS
        self.mainLayout.addWidget(
            self.imageLabel, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.mainLayout.addWidget(
            self.titleLabel, 1, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        for button in self.buttons:
            self.mainLayout.addWidget(
                button, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
            )

    #############################################
    #   EVENTS
    #################################

    def mouseDoubleClickEvent(self, mouseEvent):
        """
        Executed when the mouse is double clicked on the widget.
        By re-implementing the method, the original functionality
        is not called, and therefore double clicking no longer
        detaches the dock widget from the main window.
        :type mouseEvent: QMouseEvent
        """
        pass

    def paintEvent(self, paintEvent):
        """
        This is needed for the widget to pick the stylesheet.
        :type paintEvent: QPaintEvent
        """
        option = QtWidgets.QStyleOption()
        option.initFrom(self)
        painter = QtGui.QPainter(self)
        style = self.style()
        style.drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)
