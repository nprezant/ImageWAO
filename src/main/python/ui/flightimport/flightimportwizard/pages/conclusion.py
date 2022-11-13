from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ..transecttable import TransectTableModel
from ...flightinfoform import FlightInfoForm


class ConclusionPage(QtWidgets.QWizardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Copying...")
        self.progressBar = QtWidgets.QProgressBar(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progressBar)
        self.setLayout(layout)

        # Initialize model that gets passed from the review page
        # and flight info form that gets passed from the meta data page
        self._model = None
        self._flightInfoForm = None

        # Flag to determine when copying has completed
        self._copyFinished = False

    @QtCore.Slot(TransectTableModel)
    def updateModel(self, model):
        if model is not self._model:
            self._model = model
            self._model.copyProgress.connect(self.progressBar.setValue)
            self._model.copyComplete.connect(self._copyComplete)

    @QtCore.Slot(FlightInfoForm)
    def updateFlightInfo(self, flightInfoForm: FlightInfoForm):
        if flightInfoForm is not self._flightInfoForm:
            self._flightInfoForm = flightInfoForm

    def initializePage(self):

        # Initally the copying has not finished
        self._copyFinished = False

        # Ensure model is here
        model = self._model
        if model is None:
            print("Model must be updated for conclusion page")
            return

        # Retreive values
        libFolder = self.field("libFolder")
        flightFolder = self.field("flightFolder")

        # Construct full path and ensure it exists
        flightPath = Path(libFolder) / flightFolder
        flightPath.mkdir(exist_ok=True)

        # Copy files on other thread
        self._model.copyTransects(flightPath)

        # Write out flight import meta data
        self._flightInfoForm.save(flightPath)

    @QtCore.Slot()
    def _copyComplete(self):

        self.setTitle("Copying... Complete")

        # Tell the page that it is complete so it can update the correct buttons.
        self._copyFinished = True
        self.completeChanged.emit()

    def isComplete(self):
        return self._copyFinished

    def nextId(self):
        return -1
