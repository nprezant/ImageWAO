

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide2 import ApplicationContext

from PySide2 import QtWidgets

from imagewao import QImageWAO
from library import Library
from importers import ImportWizards
from notifications import Notifier
from imageviewer import QImageViewer
from gridviewer import QImageGridView
from progressbar import QAbsoluteProgressBar

class AppContext(ApplicationContext):

    @cached_property
    def window(self):
        return QImageWAO(
            self.mspaint,
            self.grid,
            self.library,
            self.animalAdder,
            self.animalTotals,
            self.importWizards,
            self.notifier,
            self.progressBar,
        )

    @cached_property
    def mspaint(self):
        return QImageViewer()

    @cached_property
    def progressBar(self):
        return QAbsoluteProgressBar(self.mspaint)

    @cached_property
    def grid(self):
        self.view = QImageGridView()
        return self.view

    @cached_property
    def library(self):
        return Library(self)

    @cached_property
    def animalAdder(self):
        return QtWidgets.QScrollArea()

    @cached_property
    def animalTotals(self):
        return QtWidgets.QScrollArea()

    @cached_property
    def importWizards(self):
        return ImportWizards()

    @cached_property
    def notifier(self):
        return Notifier()
    
    def run(self):
        self.window.resize(650, 350)
        self.window.show()
        return self.app.exec_()
