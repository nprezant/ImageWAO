from PySide2 import QtCore, QtWidgets

# TODO button to toggle numeric or alpha bravo etc
from ..transecttable import TransectTableModel, TransectTableView

from .ids import PageIds


class ReviewPage(QtWidgets.QWizardPage):

    modelChanged = QtCore.Signal(TransectTableView)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Review")
        self.mainLabel = QtWidgets.QLabel(
            "These are the categorized transects, in chronological order.\n"
            "Note that the geographical order, often given North to South as Alfa, Bravo, etc. "
            "is not necessarily the same as the chronological order as flown by the plane.\n\n"
            "Copy and paste the correct naming order from Excel, or enter the names manually.\n"
        )
        self.mainLabel.setWordWrap(True)

        # Loading widgets
        self.loadingLabel = QtWidgets.QLabel("Categorizing images...")
        self.progressBar = QtWidgets.QProgressBar(self)

        self.view = TransectTableView()
        self.model: TransectTableModel = self.view.model()

        self.model.categorizeProgress.connect(self.progressBar.setValue)
        self.model.categorizeSuccess.connect(self._categorizationSuccess)
        self.model.categorizeError.connect(self._categorizationError)

        buttonBox = QtWidgets.QDialogButtonBox()
        self.toggleTransectNamesButton = buttonBox.addButton(
            "Rename to numeric", QtWidgets.QDialogButtonBox.ResetRole
        )
        self.toggleTransectNamesButton.clicked.connect(self._toggleTransectNames)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.mainLabel)
        layout.addWidget(buttonBox)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Flag to note whether categorization has finished
        self._categorizationFinished = False

    @QtCore.Slot()
    def _categorizationSuccess(self):
        self.loadingLabel.setText("Categorizing images... Complete")

        # Tell the page that it is complete so it can update the correct buttons.
        self._categorizationFinished = True
        self.completeChanged.emit()

        # Ensure that the model gets renamed nicely, and share it with the other pages
        self.model.renameNATO()
        self.modelChanged.emit(self.model)

        # Adjust the size of the wizard to fit in the new data
        self.wizard().adjustSize()
        self.view.resizeColumnsToContents()

    @QtCore.Slot(tuple)
    def _categorizationError(self, e):
        self.loadingLabel.setText("Categorizing images... Error")

        QtWidgets.QMessageBox.warning(
            self.parent(),
            "Sorry, I encountered an error while categorizing!",
            str(e[1]),
        )

    def isComplete(self):
        return self._categorizationFinished

    def initializePage(self):

        # Initally the categorization has not finished
        self._categorizationFinished = False
        self.loadingLabel.setText("Categorizing images...")

        # read data from previous fields
        folder = self.field("importFolder")
        maxDelay = self.field("maxDelay")
        minCount = self.field("minCount")

        # read folder
        self.model.clearData()
        self.model.readFolder(folder, maxDelay, minCount)

    def nextId(self):
        return PageIds.Page_Metadata

    @QtCore.Slot()
    def _toggleTransectNames(self):
        if self.toggleTransectNamesButton.text() == "Rename to NATO":
            self.model.renameNATO()
            self.toggleTransectNamesButton.setText("Rename to numberic")
        else:
            self.model.renameByOrder()
            self.toggleTransectNamesButton.setText("Rename to NATO")
