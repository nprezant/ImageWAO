from PySide2 import QtWidgets

from .draglabelcontainer import DragLabelContainer


class Person(QtWidgets.QWidget):
    def __init__(self, name: str):
        super().__init__()

        self.nameLine = QtWidgets.QLineEdit(self)
        self.nameLine.setText(name)

        self.assignedTransectList = DragLabelContainer()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.nameLine)
        layout.addWidget(self.assignedTransectList)
        self.setLayout(layout)

    def addTransect(self, name: str):
        self.assignedTransectList.addDragLabel(name)
