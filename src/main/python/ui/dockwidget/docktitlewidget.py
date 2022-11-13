from PySide6 import QtWidgets, QtCore, QtGui

from base import ctx


class DockTitleWidget(QtWidgets.QWidget):
    """
    This class implements the title area of docking area widgets.
    """

    def __init__(self, title: str, icon: QtGui.QIcon, parent: QtWidgets.QDockWidget):
        """
        Initialize the widget.
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
        self.titleLabel.setMinimumWidth(1)

        # CREATE STANDARD BUTTONS
        close = QtWidgets.QPushButton(self)
        close.setIcon(ctx.closeDockIcon)
        close.setFixedSize(18, 18)
        close.clicked.connect(parent.close)
        self.buttons = [close]

        # CONFIGURE LAYOUT
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setContentsMargins(6, 4, 6, 4)
        self.setContextMenuPolicy(QtCore.Qt.PreventContextMenu)
        # self.setMinimumWidth(self.imageLabel.width())
        self.updateLayout()

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
