'''
Popup menu for the library and address bars.
'''

import sys
from PySide2 import QtCore, QtGui, QtWidgets

from tools import showInFolder


class LibraryMenu(QtWidgets.QMenu):
    '''
    Note: You must call setTargetPaths for the context
    menu to populate.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.revealAction = None

        
    def setTargetPath(self, path:str):
        '''
        This menu is based off of target paths.
        The context buttons will populate automatically.
        '''

        # Clear menu so we can add actions again
        self.clear()
        
        # Create menu actions
        if sys.platform == 'win32':
            self.revealAction = QtWidgets.QAction('Show in Explorer', self.parent())
        elif sys.platform == 'darwin':
            self.revealAction = QtWidgets.QAction('Reveal in Finder', self.parent())
        else:
            self.revealAction = QtWidgets.QAction('Show file', self.parent())

        # Connect handlers for actions
        self.revealAction.triggered.connect(lambda: showInFolder(path))

    def popup(self, *args):
        '''
        Re-implemented to show popup menu.
        Menu actions populate based on which actions have been set.
        '''

        if self.revealAction is not None:
            self.addAction(self.revealAction)
            self.addSeparator()

        return super().popup(*args)

    