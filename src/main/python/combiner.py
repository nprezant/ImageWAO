from fbs_runtime.application_context import cached_property

from PySide2 import QtCore, QtGui, QtWidgets

from imagewao import QImageWAO


class Combiner:
    def __init__(self, ctx):
        self.ctx = ctx

    @cached_property
    def window(self):
        return QImageWAO()

    def run(self):
        with open(self.ctx.get_resource("style.qss")) as f:
            sheet = f.read()
        self.ctx.app.setStyleSheet(sheet)
        self.window.resize(1050, 650)
        self.window.show()
        return self.ctx.app.exec_()
