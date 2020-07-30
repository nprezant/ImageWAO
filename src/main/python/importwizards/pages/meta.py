
from PySide2 import QtCore, QtWidgets, QtGui

from .ids import PageIds

class MetadataPage(QtWidgets.QWizardPage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle('Metadata')
        self.setSubTitle(
            'Include metadata about the flight. '
            'This will be saved alongside the transect images.'
        )

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
        layout.addRow(self.airframeLabel, self.airframeBox)
        layout.addRow(self.flightDateLabel, self.flightDateBox)
        layout.addRow(self.flightTimeLabel, self.flightTimeBox)
        layout.addRow(self.flightNotesLabel, self.flightNotesBox)
        self.setLayout(layout)
    
    def nextId(self):
        return PageIds.Page_SetLibrary

    def save(self):
        pass

