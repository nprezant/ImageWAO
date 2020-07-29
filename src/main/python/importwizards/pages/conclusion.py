
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from ..transecttable import TransectTableModel

class ConclusionPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Copying...')
        self.progressBar = QtWidgets.QProgressBar(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progressBar)
        self.setLayout(layout)

        # Initialize model that gets passed from the review page
        self._model = None

        # Initally the copying has not finished
        self._copyFinished = False

    @QtCore.Slot()
    def _copyComplete(self):
        self.setTitle('Copying... Complete')

        # Tell the page that it is complete so it can update the correct buttons.
        self._copyFinished = True
        self.completeChanged.emit()

    @QtCore.Slot(TransectTableModel)
    def updateModel(self, model):
        if not model is self._model:
            self._model = model
            self._model.copyProgress.connect(self.progressBar.setValue)
            self._model.copyComplete.connect(self._copyComplete)

    def initializePage(self):

        # ensure model is here
        model = self._model
        if model is None:
            print('Model must be updated for conclusion page')
            return

        # retreive values
        libFolder = self.field('libFolder')
        flightFolder = self.field('flightFolder')

        # construct full path
        flightPath = Path(libFolder) / flightFolder

        # copy files on other thread
        self._model.copyTransects(flightPath)

    def isComplete(self):
        return self._copyFinished

    def nextId(self):
        return -1
