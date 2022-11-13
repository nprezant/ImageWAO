from PySide6 import QtWidgets, QtCore

from .ids import PageIds

from ...flightinfoform import FlightInfoForm


class MetadataPage(QtWidgets.QWizardPage):

    flightInfoChanged = QtCore.Signal(FlightInfoForm)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Metadata")
        self.setSubTitle(
            "Include metadata about the flight. "
            "This will be saved alongside the transect images."
        )

        # Copy the layout of the flight info form
        self._flightInfoForm = FlightInfoForm()
        self.setLayout(self._flightInfoForm.layout())

        self.registerField("flightInfoForm", self._flightInfoForm)

    def _saveDefaults(self):
        self.flightInfoChanged.emit(self._flightInfoForm)

    def nextId(self):
        return PageIds.Page_SetLibrary
