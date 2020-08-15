from pathlib import Path

from PySide2 import QtWidgets, QtGui, QtCore

from .person import Person


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        buttonBox = QtWidgets.QDialogButtonBox()
        addPersonButton = buttonBox.addButton(
            "Add Person", QtWidgets.QDialogButtonBox.ResetRole
        )
        okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)

        addPersonButton.clicked.connect(lambda: self._addPerson())
        okayButton.clicked.connect(self._okPressed)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def _addPerson(self, name: str = "New Person") -> Person:
        person = Person(name)
        self.layout().insertWidget(self.layout().count() - 1, person)
        return person

    @QtCore.Slot()
    def _okPressed(self):
        # would want to save here
        self.close()

    def _clearPeople(self):
        """Clears all people from layout, leaving button box"""
        layout = self.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if not item:
                continue

            w = item.widget()
            if w and isinstance(w, Person):
                item = layout.takeAt(i)
                w.deleteLater()

    def readFlightFolder(self, flightFolder: Path):

        self._clearPeople()

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
