
import os
from pathlib import Path

from PySide2 import QtCore, QtWidgets

from transects import Transect, TransectTableModel, TransectTableView

class FlightImportWizard(QtWidgets.QWizard):

    Page_Intro = 1
    Page_Parameters = 2
    Page_Review = 3
    Page_Metadata = 4
    Page_SetLibrary = 5
    Page_Conclusion = 6

    def __init__(self):
        super().__init__()

        # Look and feel
        # this page should not have a cancel button
        self.setOption(QtWidgets.QWizard.NoCancelButton)

        # page instances
        introPage = IntroPage(self)
        parametersPage = ParametersPage(self)
        reviewPage = ReviewPage(self)
        metadataPage = MetadataPage(self)
        setLibraryPage = SetLibraryPage(self)
        conclusionPage = ConclusionPage(self)

        # connections
        reviewPage.modelChanged.connect(conclusionPage.updateModel)

        # set page numbers
        self.setPage(self.Page_Intro, introPage)
        self.setPage(self.Page_Parameters, parametersPage)
        self.setPage(self.Page_Review, reviewPage)
        self.setPage(self.Page_Metadata, metadataPage)
        self.setPage(self.Page_SetLibrary, setLibraryPage)
        self.setPage(self.Page_Conclusion, conclusionPage)

        self.setWindowTitle('Flight Import Wizard')

        # connect next button to save page defaults if applicable
        self.button(self.NextButton).clicked.connect(
            self._saveCurrentPageDefaults
        )

    def _saveCurrentPageDefaults(self):
        try:
            # have to get the PREVIOUS page
            self.page(self.visitedPages()[-2])._saveDefaults()
        except AttributeError:
            pass

class IntroPage(QtWidgets.QWizardPage):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Choose folder to import from')

        topLabel = QtWidgets.QLabel(
            'This wizard will help you import new (unsorted) '
            'aerial flight images and categorize them into their '
            'proper transects.'
        )
        topLabel.setWordWrap(True)

        self.pathLabel = QtWidgets.QLabel('Import from:')
        self.pathEdit = QtWidgets.QLineEdit()
        self.browse = QtWidgets.QPushButton('...')
        self.browse.setMaximumWidth(
            self.browse.fontMetrics().boundingRect('...').width() + 20
        )
        self.browse.clicked.connect(self._chooseImportFolder)
        self.registerField('importFolder', self.pathEdit)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(topLabel, 0, 0, 1, 3)
        layout.addWidget(self.pathLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1)
        layout.addWidget(self.browse, 1, 2)
        self.setLayout(layout)

    def initializePage(self):
        self.pathEdit.setText(str(self._defaultImportFolder))

    @property
    def _defaultImportFolder(self):
        settings = QtCore.QSettings()
        path = settings.value(
            'import/flightImportDirectory',
            Path().home().anchor
        )
        return path

    def _saveDefaults(self):

        # save default import path
        settings = QtCore.QSettings()
        settings.setValue(
            'import/flightImportDirectory', 
            self.pathEdit.text()
        )

    def _chooseImportFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            'Choose Import Folder',
            self.pathEdit.text(),
            QtWidgets.QFileDialog().ShowDirsOnly
        )

        if not folder == '':
            self.pathEdit.setText(folder)

    def nextId(self):
        return FlightImportWizard.Page_Parameters        

class ParametersPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Sorting Algorithm Parameters')

        topLabel = QtWidgets.QLabel(
            '<b>You probably don\'t need to change these.</b><br/>'
            'These parameters govern the algorithm that categorizes '
            'flight photos into transects. '
            'Hover over the descriptions for more information. '
        )
        topLabel.setWordWrap(True)

        # photo delay
        self.maxDelayLabel = QtWidgets.QLabel('Max time between photos')
        self.maxDelayLabel.setToolTip(
            'Maximum number of seconds between '
            'photos on the same transect.\n\n'
            'This will be used to determine where one transect '
            'ends and another begins.'
        )
        self.maxDelayBox = QtWidgets.QSpinBox()
        self.maxDelayBox.setRange(1,1000)
        self.maxDelayBox.setSuffix(' seconds')
        self.registerField('maxDelay', self.maxDelayBox)

        # min transect photo count
        self.minCountLabel = QtWidgets.QLabel('Min photos per transect')
        self.minCountLabel.setToolTip(
            'Minimum number of photos expected on the same transect.\n\n'
            'This number will be used to rule out one-off test images.'
        )
        self.minCountBox = QtWidgets.QSpinBox()
        self.minCountBox.setRange(1,1000)
        self.minCountBox.setSuffix(' photos')
        self.registerField('minCount', self.minCountBox)

        layout = QtWidgets.QFormLayout()
        layout.addRow(topLabel)
        layout.addRow(self.maxDelayLabel, self.maxDelayBox)
        layout.addRow(self.minCountLabel, self.minCountBox)
        self.setLayout(layout)

    def initializePage(self):
        self._setDefaults()

    def _setDefaults(self):
        settings = QtCore.QSettings()
        maxDelay = settings.value(
            'import/maxDelay', 
            5
        )
        minCount = settings.value(
            'import/minCount', 
            3
        )
        self.maxDelayBox.setValue(int(maxDelay))
        self.minCountBox.setValue(int(minCount))

    def _saveDefaults(self):
        settings = QtCore.QSettings()
        settings.setValue(
            'import/maxDelay', 
            self.maxDelayBox.value()
        )
        settings.setValue(
            'import/minCount', 
            self.minCountBox.value()
        )
    
    def nextId(self):
        return FlightImportWizard.Page_Review

class ReviewPage(QtWidgets.QWizardPage):

    modelChanged = QtCore.Signal(TransectTableView)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Review')
        self.topLabel = QtWidgets.QLabel(
            'These are the categorized transects, in chronological order.\n'
            'Note that the geographical order, often given North to South as Alpha, Bravo, etc. '
            'is not necessarily the same as the chronological order.\n\n'
            'Copy and paste the correct naming order from Excel, or enter the names manually.\n'
        )
        self.topLabel.setWordWrap(True)

        # Loading widgets
        self.loadingLabel = QtWidgets.QLabel('Categorizing images...')
        self.progressBar = QtWidgets.QProgressBar(self)

        self.view = TransectTableView()
        self.model = TransectTableModel()
        self.model.categorizeProgress.connect(self.progressBar.setValue)
        self.model.categorizeComplete.connect(self._categorizeComplete)

        self.view.setModel(self.model)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.loadingLabel)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.topLabel)
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Initally the categorization has not finished
        self._categorizationFinished = False

    @QtCore.Slot()
    def _categorizeComplete(self):
        self.loadingLabel.setText('Categorizing images... Complete')

        # Tell the page that it is complete so it can update the correct buttons.
        self._categorizationFinished = True
        self.completeChanged.emit()

        # Ensure that the model gets renamed nicely, and share it with the other pages
        self.model.renameByOrder()
        self.modelChanged.emit(self.model)

        # Adjust the size of the wizard to fit in the new data
        self.wizard().adjustSize()

    def isComplete(self):
        return self._categorizationFinished

    def initializePage(self):

        # read data from previous fields
        folder = self.field('importFolder')
        maxDelay = self.field('maxDelay')
        minCount = self.field('minCount')

        # read folder
        self.model.readFolder(folder, maxDelay, minCount)
    
    def nextId(self):
        return FlightImportWizard.Page_Metadata

class MetadataPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Metadata')

        topLabel = QtWidgets.QLabel(
            'Include metadata about the flight. '
            'This will be saved alongside the transect images.'
        )
        topLabel.setWordWrap(True)

        # airframe
        self.airframeLabel = QtWidgets.QLabel('Airframe')
        self.airframeBox = QtWidgets.QLineEdit()
        self.registerField('airframeBox', self.airframeBox)

        # flight date
        self.flightDateLabel = QtWidgets.QLabel('Flight Date')
        self.flightDateBox = QtWidgets.QLineEdit()
        self.registerField('flightDateBox', self.flightDateBox)

        # flight time
        self.flightTimeLabel = QtWidgets.QLabel('Flight Time')
        self.flightTimeBox = QtWidgets.QLineEdit()
        self.registerField('flightTimeBox', self.flightTimeBox)

        # additional notes
        self.flightNotesLabel = QtWidgets.QLabel('Additional Notes')
        self.flightNotesBox = QtWidgets.QTextEdit()
        self.registerField('flightNotesBox', self.flightNotesBox)

        layout = QtWidgets.QFormLayout()
        layout.addRow(topLabel)
        layout.addRow(self.airframeLabel, self.airframeBox)
        layout.addRow(self.flightDateLabel, self.flightDateBox)
        layout.addRow(self.flightTimeLabel, self.flightTimeBox)
        layout.addRow(self.flightNotesLabel, self.flightNotesBox)
        self.setLayout(layout)
    
    def nextId(self):
        return FlightImportWizard.Page_SetLibrary

class SetLibraryPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Copy Images')

        topLabel = QtWidgets.QLabel(
            'Choose where you want to import the images to.\n'
            'By default, this will be your flight library.'
        )
        topLabel.setWordWrap(True)

        # import to this path
        self.pathLabel = QtWidgets.QLabel('Import to')
        self.pathEdit = QtWidgets.QLineEdit()
        self.browse = QtWidgets.QPushButton('...')
        self.browse.setMaximumWidth(
            self.browse.fontMetrics().boundingRect('...').width() + 20
        )
        self.browse.clicked.connect(self._chooseImportFolder)
        self.registerField('libFolder', self.pathEdit)

        # import to this folder name
        self.flightFolderLabel = QtWidgets.QLabel('Flight folder')
        self.flightFolderLabel.setMinimumWidth (
            self.flightFolderLabel.fontMetrics().boundingRect('Flight folder ').width()
        )
        self.flightFolderBox = QtWidgets.QLineEdit('FlightXX')
        self.registerField('flightFolder', self.flightFolderBox)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(topLabel, 0, 0, 1, 3)
        layout.addWidget(self.pathLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1)
        layout.addWidget(self.browse, 1, 2)
        layout.addWidget(self.flightFolderLabel, 2, 0 ,1, 3)
        layout.addWidget(self.flightFolderBox, 2, 1, 1, 2)
        layout.setColumnMinimumWidth(0, self.flightFolderLabel.minimumWidth())
        self.setLayout(layout)

    def initializePage(self):
        self.pathEdit.setText(str(self._defaultLibraryFolder))

    @property
    def _defaultLibraryFolder(self):
        settings = QtCore.QSettings()
        path = settings.value(
            'library/homeDirectory',
            str(Path().home()).replace(os.sep, '/')
        )
        return path

    def _chooseImportFolder(self):

        # prompt user to choose folder
        folder = QtWidgets.QFileDialog().getExistingDirectory(
            self,
            'Import to ...',
            self.pathEdit.text(),
            QtWidgets.QFileDialog().ShowDirsOnly
        )

        if not folder == '':
            self.pathEdit.setText(folder)

    def nextId(self):
        return FlightImportWizard.Page_Conclusion
    
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
