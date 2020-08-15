from pathlib import Path
from typing import List

from PySide2 import QtWidgets, QtGui, QtCore

from .person import Person
from .transect import Transect


class DistributionForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        buttonBox = QtWidgets.QDialogButtonBox()
        addPersonButton = buttonBox.addButton(
            "Add Person", QtWidgets.QDialogButtonBox.ResetRole
        )
        distributeButton = buttonBox.addButton(
            "Distribute", QtWidgets.QDialogButtonBox.ResetRole
        )
        okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)

        addPersonButton.clicked.connect(lambda: self._addPerson())
        distributeButton.clicked.connect(lambda: self._distribute())
        okayButton.clicked.connect(self._okPressed)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    @QtCore.Slot()
    def _okPressed(self):
        # would want to save here
        self.close()

    def _addPerson(self, name: str = "New Person") -> Person:
        person = Person(name)
        self.layout().insertWidget(self.layout().count() - 1, person)
        return person

    def _distribute(self, newTransects: List[Transect] = None):
        """Distributes transects among existing people.
        If newTransects are passed in, these are added on
        top of existing transects. If no newTransects are passed
        in, the existing transects are re-distributed among existing people.
        """

        people = self.findChildren(Person)

        # Grab the transects from the people
        if newTransects is None:
            newTransects = []
            for person in people:
                [newTransects.append(t) for t in person.removeTransects()]

        # Sort transects by number of photos
        newTransects.sort(key=lambda x: x.numPhotos)

        # Distribute among people
        numPeople = len(people)
        i = 0
        while newTransects:
            personIndex = i % numPeople
            person = people[personIndex]
            person.addTransect(newTransects.pop())
            i += 1

    def _clearPeople(self):
        """Clears all people from layout, leaving button box"""
        layout = self.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if not item:
                continue

            w = item.widget()
            if w and isinstance(w, Person):
                layout.takeAt(i)
                w.setParent(None)
                w.deleteLater()

    def readFlightFolder(self, flightFolder: Path):

        self._clearPeople()

        self._addPerson("Lauren")
        self._addPerson("Noah")
        self._addPerson("Matt")

        # Read transect folder
        transects = Transect.createFromFlight(flightFolder)
        transects.extend(transects)

        self._distribute(transects)
