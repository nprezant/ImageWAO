from pathlib import Path
from typing import List

from PySide2 import QtWidgets, QtCore, QtGui

from base import config
from .person import Person
from .people import People
from .transect import Transect
from .twocolorgradient import TwoColorGradient
from .dragtransect import DragTransect
from .goallabel import GoalLabel


class DistributionForm(QtWidgets.QWidget):

    closeRequested = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.flightFolder = None
        self._isEditing = False
        self.transectColorGradient = TwoColorGradient(
            QtGui.QColor("#105569"), QtGui.QColor("#1fc3f0")
        )

        self.goalLabel = GoalLabel()

        # Main button box, always shown
        buttonBox = QtWidgets.QDialogButtonBox()

        self.editButton = buttonBox.addButton(
            "Edit People", QtWidgets.QDialogButtonBox.ResetRole
        )
        self.editButton.setToolTip("Add, remove, or rename people.")

        distributeButton = buttonBox.addButton(
            "Distribute", QtWidgets.QDialogButtonBox.ResetRole
        )
        distributeButton.setToolTip(
            "Sorts all transects largest to smallest, then assigns"
            "\nthem one by one to each person."
        )
        okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)
        applyButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Apply)

        self.editButton.clicked.connect(self._toggleEditing)

        distributeButton.clicked.connect(lambda: self._distribute())
        okayButton.clicked.connect(self._okPressed)
        applyButton.clicked.connect(self._save)

        # Button box for editing and adding new rows and stuff
        self.editButtonBox = QtWidgets.QDialogButtonBox()
        addPersonButton = self.editButtonBox.addButton(
            "Add Person", QtWidgets.QDialogButtonBox.ResetRole
        )
        addPersonButton.setStyleSheet(
            "background-color: green; color: white; font-weight: bold;"
        )
        # intentionally lambda expression to allow default parameters
        addPersonButton.clicked.connect(lambda: self._addNewPerson())

        resetButton = self.editButtonBox.addButton(
            "Reset", QtWidgets.QDialogButtonBox.ResetRole
        )
        resetButton.setToolTip("Reset form to it's original state")
        # intentionally lambda expression to allow default parameters
        resetButton.clicked.connect(lambda: self._reset())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.goalLabel)
        layout.addStretch()
        layout.addWidget(self.editButtonBox)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    @QtCore.Slot()
    def _okPressed(self):
        success = self._save()
        if success:
            self.closeRequested.emit()

    @QtCore.Slot()
    def _save(self) -> bool:
        """Saves form. If successful, returns True."""
        if self.flightFolder is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Distribution Form",
                "Cannot save data when no flight folder is specified."
                " Please open this form by right clicking on a flight folder"
                " and selecting 'distribute flight'.",
            )
            return False
        else:
            people = People(self._people())
            people.dump(config.flightDistributionFile(self.flightFolder))
            return True

    def _addNewPerson(self, name: str = "New Person"):
        person = Person(name)
        self._addPerson(person)

    def _addPerson(self, person: Person):
        person.numPhotosUpdated.connect(self._recolorPhotoSums)
        person.requestToBeDeleted.connect(lambda: self._deletePersonRequested(person))
        self.layout().insertWidget(self.layout().count() - 3, person)
        self._updateCountsPerPerson()

    def _distribute(self, newTransects: List[Transect] = None):
        """Distributes transects among existing people.
        If newTransects are passed in, these are added on
        top of existing transects. If no newTransects are passed
        in, the existing transects are re-distributed among existing people.
        """

        people: List[Person] = self._people()

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

        # Color transects by their weight in photos
        # Necessary because we just re-created all the drag transect objects
        self._recolorTransects()

    def _updateCountsPerPerson(self, people=None):
        """Update the number of photos value for each person
        Objects sometimes take a while to be deleted, so it can be helpful
        to pass in the list of people you want updated.
        """
        if people is None:
            people = self._people()
        totalNumPhotos = sum(p.numPhotos() for p in people)
        meanPhotosPerPerson = int(totalNumPhotos / len(people))
        self.goalLabel.setGoal(meanPhotosPerPerson)
        [p.updateNumPhotos(meanPhotosPerPerson) for p in people]

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
        self._setEditable(False)

    def _loadSaveFile(self, saveFile: Path):
        self._clearPeople()
        people = People.loadFromFile(saveFile)
        for person in people:
            self._addPerson(person)
        self._updateCountsPerPerson()
        self._recolorTransects()

    def _reset(self):
        if self.flightFolder is not None:
            answer = QtWidgets.QMessageBox.warning(
                self,
                "ImageWAO",
                "Are you sure you want to reset?"
                "\n\nThis operation will remove all but four people and re-populate the transects based on this flight's file structure.",
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel,
            )
            if answer & QtWidgets.QMessageBox.Ok:
                self._loadFromFileStructure(self.flightFolder)

    def _loadFromFileStructure(self, flightFolder: Path):
        self._clearPeople()

        # Need at least four people for this to make any sense
        self._addNewPerson("Joe")
        self._addNewPerson("Matt")
        self._addNewPerson("Josh")
        self._addNewPerson("Pawel")

        # Read transect folder
        transects = Transect.createFromFlight(flightFolder)
        transects.extend(transects)

        # Distribute transects among the people
        self._distribute(transects)

    def _people(self):
        return self.findChildren(Person)

    def _recolorPhotoSums(self, people=None):
        if people is None:
            people: List[Person] = self._people()
        people.sort(key=lambda p: p.numPhotos())

        leastPhotos = people[0].numPhotos()
        mostPhotos = people[-1].numPhotos()

        for p in people:
            if p.numPhotos() == leastPhotos:
                p.numPhotosLabel.setBackgroundColor(self.transectColorGradient.end)
            elif p.numPhotos() == mostPhotos:
                p.numPhotosLabel.setBackgroundColor(self.transectColorGradient.start)
            else:
                p.numPhotosLabel.clearStyle()

    def _recolorTransects(self):
        dragTransects: List[DragTransect] = self.findChildren(DragTransect)
        dragTransects.sort(key=lambda t: t.numPhotos())

        leastPhotos = dragTransects[0].numPhotos()
        mostPhotos = dragTransects[-1].numPhotos()
        diff = mostPhotos - leastPhotos

        for dragTransect in dragTransects:
            numPhotos = dragTransect.numPhotos()
            percentage = (numPhotos - leastPhotos) / diff
            color = self.transectColorGradient.getColor(percentage)
            dragTransect.setBackgroundColor(color)

    def _toggleEditing(self):
        if not self._isEditing:
            # We were not editing, so now we need to switch to the editing menu
            self._setEditable(True)
        else:
            # We were just editing, now we need to switch back to the default
            self._setEditable(False)

    def _setEditable(self, editable: bool):
        """Sets the form up for editing people names and such"""
        if editable:
            [p.setEditable(True) for p in self._people()]
            self.editButton.setText("Done Editing")
            self.editButtonBox.show()
            self._isEditing = True
        else:
            [p.setEditable(False) for p in self._people()]
            self.editButton.setText("Edit Names")
            self.editButtonBox.hide()
            self._isEditing = False

    def _deletePersonRequested(self, person: Person):
        # Cannot remove if there are too few people
        people = self._people()
        if len(people) <= 2:
            QtWidgets.QMessageBox.warning(
                self,
                "ImageWAO",
                "Cannot distribute transects between less than two (2) people.",
            )

        else:
            # Remove transects from this person and re-purpose
            personsTransects: List[Transect] = [
                dragTransect.transect for dragTransect in person.removeTransects()
            ]

            # Closing the widget will also delete it
            person.close()
            people.remove(person)

            # Want to give transects to people who have the least
            people.sort(key=lambda p: p.numPhotos())

            # Distribute among people
            numPeople = len(people)
            i = 0
            while personsTransects:
                personIndex = i % numPeople
                tempPerson: Person = people[personIndex]
                if not tempPerson.contains(personsTransects[-1]):
                    tempPerson.addTransect(personsTransects.pop())
                i += 1

            # Ensure good order for transects
            [p.sortTransects() for p in people]

            # Update counts for each person
            self._updateCountsPerPerson(people)
            self._recolorPhotoSums(people)

            # Color transects by their weight in photos
            # Necessary because we just re-created some of the drag transect objects
            self._recolorTransects()
