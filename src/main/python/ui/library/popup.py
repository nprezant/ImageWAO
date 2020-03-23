'''
Popup menu for the library and address bars.
'''

import sys
from PySide2 import QtCore, QtGui, QtWidgets

from importers import FlightImportWizard
from tools import showInFolder


class LibraryMenu(QtWidgets.QMenu):
    '''
    Note: You must call setTargetPaths for the context
    menu to populate.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.revealAction = None
        self.importWizardAction = None
        
    def reset(self):
        self.revealAction = None
        self.importWizardAction = None
        
    def setTargetPath(self, path:str):
        '''
        This menu is based off of target paths.
        The context buttons will populate automatically.
        '''
        
        # Create menu actions
        if sys.platform == 'win32':
            self.revealAction = QtWidgets.QAction('Show in Explorer', self.parent())
        elif sys.platform == 'darwin':
            self.revealAction = QtWidgets.QAction('Reveal in Finder', self.parent())
        else:
            self.revealAction = QtWidgets.QAction('Show file', self.parent())

        # Connect handlers for actions
        self.revealAction.triggered.connect(lambda: showInFolder(path))

    def enableImportWizard(self):
        '''
        Creates the import wizard action. Will be added to the menu during `popup()`
        '''
        self.importWizardAction = QtWidgets.QAction('Import new images', self.parent())
        self.importWizardAction.triggered.connect(FlightImportWizard.openNew)

    def popup(self, *args):
        '''
        Re-implemented to show popup menu.
        Menu actions populate based on which actions have been set.
        '''

        self.clear()

        if self.revealAction is not None:
            self.addAction(self.revealAction)
            self.addSeparator()

        if self.importWizardAction is not None:
            self.addAction(self.importWizardAction)
            self.addSeparator()

        self.reset()
        return super().popup(*args)

    