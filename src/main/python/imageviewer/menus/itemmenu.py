'''
The menu for the popup that displays on graphic items.
'''

from PySide2 import QtCore, QtGui, QtWidgets

class ItemMenu(QtWidgets.QMenu):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.editAction = None
        self.deleteAction = None
        
    def reset(self):
        self.editAction = None
        self.deleteAction = None

    def addShapeItem(self, shape):
        pass

    def popup(self, *args):
        '''
        Re-implemented to show popup menu.
        Menu actions populate based on which actions have been set.
        '''

        self.clear()

        if self.editAction is not None:
            self.addAction(self.editAction)
            self.addSeparator()

        if self.deleteAction is not None:
            self.addAction(self.deleteAction)
            self.addSeparator()

        self.addAction(QtWidgets.QAction('test', self.parent()))

        self.reset()
        return super().popup(*args)


