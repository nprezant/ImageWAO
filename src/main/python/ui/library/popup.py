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
        
    def setTargetPaths(self, paths:list):
        '''
        This menu is based off of target paths.
        The context buttons will populate automatically.
        '''

        # Clear menu so we can add actions again
        self.clear()
        
        # Create menu actions
        if sys.platform == 'win32':
            showAction = QtWidgets.QAction('Show in Explorer', self.parent())
        elif sys.platform == 'darwin':
            showAction = QtWidgets.QAction('Reveal in Finder', self.parent())
        else:
            showAction = QtWidgets.QAction('Show file', self.parent())

        # Connect handlers for actions
        showAction.triggered.connect(lambda: showInFolder(paths[0]))

        # Add actions to the menu
        self.addAction(showAction)

    