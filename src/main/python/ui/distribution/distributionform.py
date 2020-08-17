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
            "Edit Names", QtWidgets.QDialogButtonBox.ResetRole
        )
        distributeButton = buttonBox.addButton(
            "Distribute", QtWidgets.QDialogButtonBox.ResetRole
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

        # intentionally lambda expression to allow default parameters
        addPersonButton.clicked.connect(lambda: self._addNewPerson())
        self.editButtonBox.hide()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.goalLabel)
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
        self.layout().insertWidget(self.layout().count() - 2, person)

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

    def _updateCountsPerPerson(self):
        """Update the number of photos value for each person"""
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

    def _loadSaveFile(self, saveFile: Path):
        self._clearPeople()
        people = People.loadFromFile(saveFile)
        for person in people:
            self._addPerson(person)
        self._updateCountsPerPerson()
        self._recolorTransects()

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

    def _people(self):
        return self.findChildren(Person)

    def _recolorPhotoSums(self):
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
        if self._isEditing:
            # We were just editing, now we need to switch back to the default
            self.editButton.setText("Edit Names")
            self.editButtonBox.hide()
            self._isEditing = False
        else:
            # Now we need to switch to the editing menu
            self.editButton.setText("Done Editing")
            self.editButtonBox.show()
            self._isEditing = True
