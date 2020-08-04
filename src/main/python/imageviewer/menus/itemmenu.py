"""
The menu for the popup that displays on graphic items.
"""

from PySide2 import QtWidgets


class ItemMenu(QtWidgets.QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.editAction: QtWidgets.QAction = None
        self.deleteAction: QtWidgets.QAction = None

    def reset(self):
        self.editAction = None
        self.deleteAction = None

    def addEditableItem(self, item, editSlot, text="Edit"):
        self.editAction = QtWidgets.QAction(text, self.parent())
        self.editAction.triggered.connect(editSlot)

    def addDeletableItem(self, item, deleteSlot, text="Delete"):
        self.deleteAction = QtWidgets.QAction(text, self.parent())
        self.deleteAction.triggered.connect(deleteSlot)

    def popup(self, *args):
        """
        Re-implemented to show popup menu.
        Menu actions populate based on which actions have been set.
        """

        self.clear()

        if self.editAction is not None:
            self.addAction(self.editAction)
            self.addSeparator()

        if self.deleteAction is not None:
            self.addAction(self.deleteAction)
            self.addSeparator()

        self.reset()
        return super().popup(*args)
