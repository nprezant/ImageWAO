
from pathlib import Path

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import (
    QWidget, QPushButton, QLineEdit, QLabel, QSpinBox,
    QFormLayout, QGridLayout, QSizePolicy, QFileDialog,
    QWizard, QWizardPage, QAction, QVBoxLayout,
    QTableView, QTextEdit, 
)

from base import TransectTableModel, TransectTableView

class FlightImportWizard(QWizard):

    Page_Intro = 1
    Page_Parameters = 2
    Page_Review = 3
    Page_Metadata = 4
    Page_ChangeLibrary = 5
    Page_Conclusion = 6

    def __init__(self):
        super().__init__()

        self.setPage(self.Page_Intro, IntroPage(self))
        self.setPage(self.Page_Parameters, ParametersPage(self))
        self.setPage(self.Page_Review, ReviewPage(self))
        self.setPage(self.Page_Metadata, MetadataPage(self))
        self.setPage(self.Page_ChangeLibrary, ChangeLibraryPage(self))
        self.setPage(self.Page_Conclusion, ConclusionPage(self))

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

class IntroPage(QWizardPage):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Introduction')

        topLabel = QLabel(
            'This wizard will help you import new (unsorted) '
            'aerial flight images and categorize them into their '
            'proper transects.'
        )
        topLabel.setWordWrap(True)

        self.pathLabel = QLabel('Import from:')
        self.pathEdit = QLineEdit()
        self.browse = QPushButton('...')
        self.browse.setMaximumWidth(
            self.browse.fontMetrics().boundingRect('...').width() + 20
        )
        self.browse.clicked.connect(self._chooseImportFolder)
        self.registerField('importFolder', self.pathEdit)

        layout = QGridLayout()
        layout.addWidget(topLabel, 0, 0, 1, 3)
        layout.addWidget(self.pathLabel, 1, 0)
        layout.addWidget(self.pathEdit, 1, 1)
        layout.addWidget(self.browse, 1, 2)
        self.setLayout(layout)

    def initializePage(self):
        self.pathEdit.setText(str(self._defaultImportFolder))

    @property
    def _defaultImportFolder(self):
        settings = QSettings()
        path = settings.value(
            'import/flightImportDirectory',
            Path().home().anchor
        )
        return path

    def _saveDefaults(self):

        # save default import path
        settings = QSettings()
        settings.setValue(
            'import/flightImportDirectory', 
            self.pathEdit.text()
        )

    def _chooseImportFolder(self):

        # prompt user to choose folder
        folder = QFileDialog().getExistingDirectory(
            self,
            'Choose Import Folder',
            self._defaultImportFolder,
            QFileDialog().DontUseNativeDialog # allows user to see files too
        )

        if not folder == '':
            self.pathEdit.setText(folder)

    def nextId(self):
        return FlightImportWizard.Page_Parameters        

class ParametersPage(QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Parameters')

        topLabel = QLabel(
            '<b>You probably don\'t need to change these.</b><br/>'
            'These parameters govern the algorithm that categorizes '
            'flight photos into transects. '
            'Hover over the descriptions for more information. '
        )
        topLabel.setWordWrap(True)

        # photo delay
        self.maxDelayLabel = QLabel('Max time between photos')
        self.maxDelayLabel.setToolTip(
            'Maximum number of seconds between '
            'photos on the same transect.\n\n'
            'This will be used to determine where one transect '
            'ends and another begins.'
        )
        self.maxDelayBox = QSpinBox()
        self.maxDelayBox.setRange(1,1000)
        self.maxDelayBox.setSuffix(' seconds')
        self.registerField('maxDelay', self.maxDelayBox)

        # min transect photo count
        self.minCountLabel = QLabel('Min photos per transect')
        self.minCountLabel.setToolTip(
            'Minimum number of photos expected on the same transect.\n\n'
            'This number will be used to rule out test images.'
        )
        self.minCountBox = QSpinBox()
        self.minCountBox.setRange(1,1000)
        self.minCountBox.setSuffix(' photos')
        self.registerField('minCount', self.minCountBox)

        layout = QFormLayout()
        layout.addRow(topLabel)
        layout.addRow(self.maxDelayLabel, self.maxDelayBox)
        layout.addRow(self.minCountLabel, self.minCountBox)
        self.setLayout(layout)

    def initializePage(self):
        self._setDefaults()

    def _setDefaults(self):
        settings = QSettings()
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
        settings = QSettings()
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

class ReviewPage(QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Review')

        self.view = TransectTableView()
        self.model = TransectTableModel()

        self.view.setModel(self.model)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def initializePage(self):

        # read data from previous fields
        folder = self.field('importFolder')
        maxDelay = self.field('maxDelay')
        minCount = self.field('minCount')

        # read folder
        self.model.readFolder(folder, maxDelay, minCount)
    
    def nextId(self):
        return FlightImportWizard.Page_Metadata

class MetadataPage(QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Metadata')

        topLabel = QLabel(
            'Include metadata about the flight. '
            'This will be saved alongside the transect images.'
        )
        topLabel.setWordWrap(True)

        # airframe
        self.airframeLabel = QLabel('Airframe')
        self.airframeBox = QLineEdit()
        self.registerField('airframeBox', self.airframeBox)

        # flight date
        self.flightDateLabel = QLabel('Flight Date')
        self.flightDateBox = QLineEdit()
        self.registerField('flightDateBox', self.flightDateBox)

        # flight time
        self.flightTimeLabel = QLabel('Flight Time')
        self.flightTimeBox = QLineEdit()
        self.registerField('flightTimeBox', self.flightTimeBox)

        # additional notes
        self.flightNotesLabel = QLabel('Additional Notes')
        self.flightNotesBox = QTextEdit()
        self.registerField('flightNotesBox', self.flightNotesBox)

        layout = QFormLayout()
        layout.addRow(topLabel)
        layout.addRow(self.airframeLabel, self.airframeBox)
        layout.addRow(self.flightDateLabel, self.flightDateBox)
        layout.addRow(self.flightTimeLabel, self.flightTimeBox)
        layout.addRow(self.flightNotesLabel, self.flightNotesBox)
        self.setLayout(layout)
    
    def nextId(self):
        return FlightImportWizard.Page_Conclusion

class ChangeLibraryPage(QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Change Library')
    
    def nextId(self):
        return FlightImportWizard.Page_Conclusion

class ConclusionPage(QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Import!')
    
    def nextId(self):
        return -1
