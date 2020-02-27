

from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide2 import ApplicationContext

from PySide2 import QtCore, QtGui, QtWidgets

from imagewao import QImageWAO
from library import Library
from importers import ImportWizards
from notifications import Notifier
from imageviewer import QImageEditor
from gridviewer import QImageGridView
from progressbar import QAbsoluteProgressBar

class AppContext(ApplicationContext):

    @cached_property
    def window(self):
        return QImageWAO(
            self,
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
        return QImageEditor()

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

    # Cached images
    @cached_property
    def defaultDockIcon(self):
        return QtGui.QIcon(self.get_resource('icons/ic_storage.png'))

    @cached_property
    def closeDockIcon(self):
        return QtGui.QIcon(self.get_resource('icons/ic_close.png'))

    def run(self):
        with open(self.get_resource('style.qss')) as f:
            sheet = f.read()
        self.app.setStyleSheet(sheet)
        self.window.resize(1050, 650)
        self.window.show()
        return self.app.exec_()
