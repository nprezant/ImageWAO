from pathlib import Path
from typing import List

from PySide2 import QtWidgets, QtGui, QtCore

from .person import Person


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        vBoxLayout = QtWidgets.QVBoxLayout()
        self.setLayout(vBoxLayout)

    def _addPerson(self, name: str) -> Person:
        person = Person(name)
        self.layout().addWidget(person)
        return person

    def readFlightFolder(self, flightFolder: Path):

        l = self._addPerson("Lauren")
        n = self._addPerson("Noah")
        m = self._addPerson("Matt")

        for fp in flightFolder.iterdir():
            if fp.is_file() or fp.name[0] == ".":
                continue
            else:
                l.addTransect(fp.name)
                n.addTransect(fp.name)
                m.addTransect(fp.name)
