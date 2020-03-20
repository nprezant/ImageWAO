

from fbs_runtime.application_context import cached_property

from PySide2 import QtCore, QtGui, QtWidgets

from imagewao import QImageWAO
from importers import ImportWizards
from imageviewer import QImageEditor
from gridviewer import QImageGridView

class Combiner:

    def __init__(self, ctx):
        self.ctx = ctx

    @cached_property
    def window(self):
        return QImageWAO(
            self.mspaint,
            self.grid,
            self.animalAdder,
            self.animalTotals,
            self.importWizards,
        )

    @cached_property
    def mspaint(self):
        return QImageEditor()

    @cached_property
    def grid(self):
        return QImageGridView()

    @cached_property
    def animalAdder(self):
        return QtWidgets.QScrollArea()

    @cached_property
    def animalTotals(self):
        return QtWidgets.QScrollArea()

    @cached_property
    def importWizards(self):
        return ImportWizards()

    def run(self):
        with open(self.ctx.get_resource('style.qss')) as f:
            sheet = f.read()
        self.ctx.app.setStyleSheet(sheet)
        self.window.resize(1050, 650)
        self.window.show()
        return self.ctx.app.exec_()
