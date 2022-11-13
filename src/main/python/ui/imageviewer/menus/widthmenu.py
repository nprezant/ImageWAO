from PySide6 import QtWidgets, QtCore


class WidthMenu(QtWidgets.QMenu):

    # When the width is changed, the new width will be emitted
    # from this signal
    widthChanged = QtCore.Signal(int)

    def __init__(self, values, defaultValue):
        """
        Create and assign menu actions with icons corresponding
        to the input iterable of width integer values
        """
        super().__init__()
        self.actions = []
        self._activeIndex = 0
        for v in values:

            action = QtWidgets.QAction(str(v))
            action.setCheckable(True)
            action.width = v
            action.triggered.connect(self.handleSelectionChanged)
            self.actions.append(action)
            self.addAction(action)

        # Initialize the default active index, or
        # simply the first index if the default is not found.
        try:
            self._activeIndex = values.index(defaultValue)
        except ValueError:
            self._activeIndex = 0

        # Check the currently active item
        self.actions[self._activeIndex].setChecked(True)

    @property
    def activeWidth(self):
        return self.actions[self._activeIndex].width

    def emitActiveWidth(self):
        """
        Trigger an emit for the active index.
        This method is used internally, but can also be called externally
        to manually emit the colorChanged signal on the active index.
        This can be helpful when initializing the class after setting up
        the proper slots.
        """
        self.widthChanged.emit(self.activeWidth)

    def handleSelectionChanged(self, checked):

        # If we tried to uncheck an item, don't allow it
        if checked is False:
            self.actions[self._activeIndex].setChecked(True)
            return

        # Uncheck the previously active index
        self.actions[self._activeIndex].setChecked(False)

        # Find the new active action, change the active index,
        # and emit the new width
        for i, a in enumerate(self.actions):
            if a.isChecked():
                self._activeIndex = i
                self.emitActiveWidth()
                return
