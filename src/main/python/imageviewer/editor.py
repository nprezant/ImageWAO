
from PySide2 import QtCore, QtGui, QtWidgets

from .imageviewer2 import QImageViewer
from .controls import ImageController


class QImageEditor(QImageViewer):

    def __init__(self):
        super().__init__()

        # Editor can have several selector states.
        # Normal (default -- whatever the QImageViewer does)
        # Zoom (User can zoom with the bounding rubber band box)
        # Drawing (User can draw on image with specified shape)

        # Controller (Toolbar, file menu, etc.)
        self.controller = ImageController(self)
        
    @property
    def toolbar(self):
        '''
        Alias for self.controller.toolbar
        '''
        return self.controller.toolbar
        

    