from pathlib import Path
from typing import List

from PySide2 import QtWidgets, QtCore

from base import config
from .person import Person
from .people import People
from .transect import Transect


class DistributionForm(QtWidgets.QWidget):

    closeRequested = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.flightFolder = None

        buttonBox = QtWidgets.QDialogButtonBox()
        addPersonButton = buttonBox.addButton(
            "Add Person", QtWidgets.QDialogButtonBox.ResetRole
        )
        distributeButton = buttonBox.addButton(
            "Distribute", QtWidgets.QDialogButtonBox.ResetRole
        )
        resetButton = buttonBox.addButton("Reset", QtWidgets.QDialogButtonBox.ResetRole)
        okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)

        addPersonButton.clicked.connect(lambda: self._addNewPerson())
        distributeButton.clicked.connect(lambda: self._distribute())
        resetButton.clicked.connect(lambda: self._reset())
        okayButton.clicked.connect(self._okPressed)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    @QtCore.Slot()
    def _okPressed(self):
        if self.flightFolder is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Distribution Form",
                "Cannot save data when no flight folder is specified."
                " Please open this form by right clicking on a flight folder"
                " and selecting 'distribute flight'.",
            )
        else:
            people = People(self.findChildren(Person))
            people.dump(config.flightDistributionFile(self.flightFolder))
            self.closeRequested.emit()

    def _addNewPerson(self, name: str = "New Person"):
        person = Person(name)
        self._addPerson(person)

    def _addPerson(self, person: Person):
        self.layout().insertWidget(self.layout().count() - 1, person)

    def _distribute(self, newTransects: List[Transect] = None):
        """Distributes transects among existing people.
        If newTransects are passed in, these are added on
        top of existing transects. If no newTransects are passed
        in, the existing transects are re-distributed among existing people.
        """

        people: List[Person] = self.findChildren(Person)

        # Grab the transects from the people
        if newTransects is None:
            newTransects: List[Transect] = []
            for person in people:
                [
                    newTransects.append(dragTransect.transect)
                    for dragTransect in person.removeTransects()
                ]

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

        # Update counts for each person
        self._updateCountsPerPerson()

    def _updateCountsPerPerson(self):
        """Update the number of photos value for each person"""
        [p.updateNumPhotos() for p in self.findChildren(Person)]

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

    def openFlightFolder(self, flightFolder: Path):
        self.flightFolder = flightFolder

        saveFile = config.flightDistributionFile(flightFolder)
        if saveFile.exists():
            self._loadSaveFile(saveFile)
        else:
            self._loadFromFileStructure(flightFolder)

    def _loadSaveFile(self, saveFile: Path):
        self._clearPeople()
        people = People.loadFromFile(saveFile)
        for person in people:
            self._addPerson(person)
        self._updateCountsPerPerson()

    def _reset(self):
        if self.flightFolder is not None:
            self._loadFromFileStructure(self.flightFolder)

    def _loadFromFileStructure(self, flightFolder: Path):
        self._clearPeople()

        # Default people. Need at least two for this to make any sense
        self._addNewPerson("Josh")
        self._addNewPerson("Pawel")

        # Read transect folder
        transects = Transect.createFromFlight(flightFolder)
        transects.extend(transects)

        # Distribute transects among the people
        self._distribute(transects)
