
from pathlib import Path

from PySide2 import QtCore

class Configuration:

    def __init__(self):

        # Files and folders in the "Flight" directory.
        # E.g. Flight01/.flight/meta.json
        self.flightDataFolder = '.flight/'
        self.flightMetaFile = '.flight/meta.json'
        self.flightDistributionFile = '.flight/distribution.json'

        # Files and folders in each transect directory
        self.markedImageFolder = '.marked/'
        self.markedDataFile = '.marked/data.transect'
        self.transectMigrationLog = '.marked/migration.log'

        # Default library directory
        self.defaultLibraryDirectory = Path.home() / 'Pictures/ImageWAO'

        # Supported image types
        self.supportedImageExtensions = ('.JPG', '.jpg', '.JPEG', '.jpeg')

        # Drawing colors
        self.colors = [
            'Teal',
            'Blue',
            'DarkGreen',
            'Red',
            'Orange',
            'Magenta',
            'Black',
            'White',
        ]

        # Drawing widths
        self.drawingWidths = [
            10,
            20,
            30,
            40,
            50,
            60,
            70,
        ]
        self.defaultWidth = 40

        # Searchable animals
        self.searchableAnimals = [
            'Baboon',
            'Donkey',
            'Eland',
            'Elephant',
            'Gemsbok',
            'Giraffe',
            'Hartebeest',
            'Horse',
            'Human',
            'Impala',
            'Jackal',
            'Kudu',
            'Ostrich',
            'Rhino',
            'Springbok',
            'Steenbok',
            'Warthog',
            'Waterbuck',
            'Zebra',
        ]

        # Threshold for resizing image grids
        self.gridImageUpdateWidth = 25
        self.gridImageMargin = 2

        # Button sizes
        self.toolbuttonSize = (20,20)

    @property
    def username(self):
        settings = QtCore.QSettings()
        return settings.value('config/username', '')

    @username.setter
    def username(self, value):
        settings = QtCore.QSettings()
        settings.setValue('config/username', value)

config = Configuration()
