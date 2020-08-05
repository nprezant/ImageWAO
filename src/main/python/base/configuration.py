from pathlib import Path

from PySide2 import QtCore

from .version import Version


class Configuration:
    def __init__(self):

        # Invalid path characters (windows allows more than this but better safe than sorry)
        self.invalidPathCharacters = "/!@#$%^&*`'\"\\}{[]?:;+=|<>"

        # Files and folders on a top (meta) level. E.g. database version.
        self.imageWaoMetaFolderName = ".imagewao"

        # Files and folders in the "Flight" directory.
        # E.g. Flight01/.flight/meta.json
        self.flightDataFolderName = ".flight"

        # Files and folders in each transect directory
        self.markedImageFolderName = ".marked"

        # Default library directory
        self.defaultLibraryDirectory = Path.home() / "Pictures/ImageWAO"

        # Supported image types
        self.supportedImageExtensions = (".JPG", ".jpg", ".JPEG", ".jpeg")

        # Drawing colors
        self.colors = [
            "Teal",
            "Blue",
            "DarkGreen",
            "Red",
            "Orange",
            "Magenta",
            "Black",
            "White",
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
            "Baboon",
            "Donkey",
            "Eland",
            "Elephant",
            "Gemsbok",
            "Giraffe",
            "Hartebeest",
            "Horse",
            "Human",
            "Impala",
            "Jackal",
            "Kudu",
            "Ostrich",
            "Rhino",
            "Springbok",
            "Steenbok",
            "Warthog",
            "Waterbuck",
            "Zebra",
        ]

        # Threshold for resizing image grids
        self.gridImageUpdateWidth = 25
        self.gridImageMargin = 2

        # Button sizes
        self.toolbuttonSize = (20, 20)

    # ImageWAO data files

    def _imageWaoMetaFolder(self):
        folder = Path(self.libraryDirectory) / self.imageWaoMetaFolderName
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def _versionFile(self):
        return self._imageWaoMetaFolder() / "version.txt"

    def projectVersion(self) -> Version:
        """Gets the project version as defined in the library folder"""

        # If the version file doesn't exist, assume 0.0.0
        if not self._versionFile().exists():
            self.setProjectVersion(Version(0, 0, 0))
            return Version(0, 0, 0)

        # The version file does exist, read it
        with open(self._versionFile(), "r") as f:
            versionString = f.readline()
        return Version.fromString(versionString)

    def setProjectVersion(self, version: Version):
        """Writes the project version to the library folder"""
        self._versionFile().touch(exist_ok=True)
        with open(self._versionFile(), "w") as f:
            f.write(version.toString())

    def logFolder(self):
        folder = self._imageWaoMetaFolder / "logs"
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    # Flight Data Files

    def flightDataFolder(self, flightFolder):
        return Path(flightFolder) / self.flightDataFolderName

    def flightMetaFile(self, flightFolder):
        return self.flightDataFolder(flightFolder) / "meta.json"

    def flightDistributionFile(self, flightFolder):
        return self.flightDataFolder(flightFolder) / "distribution.json"

    # Marked folder (within transect)

    def markedFolder(self, transectFolder):
        return Path(transectFolder) / self.markedImageFolderName

    def markedDataFile(self, transectFolder):
        return self.markedFolder(transectFolder) / "data.transect"

    def transectMigrationLog(self, transectFolder):
        return self.markedFolder(transectFolder) / "migration.log"

    @property
    def username(self):
        settings = QtCore.QSettings()
        return settings.value("config/username", "")

    @username.setter
    def username(self, value):
        settings = QtCore.QSettings()
        settings.setValue("config/username", value)

    @property
    def libraryDirectory(self):
        settings = QtCore.QSettings()
        return settings.value(
            "library/homeDirectory", str(self.defaultLibraryDirectory)
        )

    @libraryDirectory.setter
    def libraryDirectory(self, value):
        settings = QtCore.QSettings()
        settings.setValue("library/homeDirectory", value)

    @property
    def flightImportFolder(self):
        settings = QtCore.QSettings()
        return settings.value("import/flightImportDirectory", Path().home().anchor)

    @flightImportFolder.setter
    def flightImportFolder(self, value):
        settings = QtCore.QSettings()
        settings.setValue("import/flightImportDirectory", value)

    @property
    def maxPhotoDelay(self):
        settings = QtCore.QSettings()
        return settings.value("import/maxPhotoDelay", 5)

    @maxPhotoDelay.setter
    def maxPhotoDelay(self, value):
        settings = QtCore.QSettings()
        settings.setValue("import/maxPhotoDelay", value)

    @property
    def minPhotosPerTransect(self):
        settings = QtCore.QSettings()
        return settings.value("import/minPhotosPerTransect", 3)

    @minPhotosPerTransect.setter
    def minPhotosPerTransect(self, value):
        settings = QtCore.QSettings()
        settings.setValue("import/minPhotosPerTransect", value)


config = Configuration()
