
from .flight import FlightImportWizard

class ImportWizards:

    def __init__(self):
        self._flight = None

    def openNewFlight(self):
        self._flight = FlightImportWizard()
        self._flight.open()

    