from collections import UserList, OrderedDict
from pathlib import Path
import json

from base import config

from .transectdata import TransectData
from .transectdatagroup import TransectDataGroup


class TransectDataGroupList(UserList):
    """
    This class manages multiple transect save files and
    provides easy access methods for displaying and
    summarizing the data.

    `data` is a list of `TransectData`
    """

    def __init__(self, initlist=[]):
        super().__init__(initlist)

        # Used for internal optimization
        self._groupedDict = None

    def load(self, fp, groupName=None):
        """
        Loads a save file into this collection of save files.
        Specify the `groupName` if you want to group the save
        data any particular way.
        """
        self.data.append(TransectDataGroup(groupName, TransectData.load(fp)))

    def clipboardText(self):
        """
        Returns a string that can be copied and pasted into excel/notepad
        """
        s = "Flight\tAircraft\tTransect\tImage\tSpecies\tNumber\tIsDuplicate\tNotes\tUser"

        for saveGroup in self.data:
            datafp = saveGroup.saveData.fp  # data.transect file path

            # Extract flight folder and transect folder
            rel = datafp.relative_to(config.libraryDirectory)
            flight = rel.parts[0]
            transect = rel.parts[1]

            # Extract metadata info
            metadataFile: Path = config.flightMetaFile(
                Path(config.libraryDirectory) / flight
            )
            if metadataFile.exists():
                with open(metadataFile, "r") as f:
                    metadata = json.load(f)
                try:
                    airframe = metadata["Airframe"]
                except KeyError:
                    raise KeyError(
                        "'Airframe' key not found in meta data file."
                        " This should not happen."
                    )
            else:
                airframe = ""

            # Combine into string
            for imageName, countData in saveGroup.saveData.imageCounts():
                isDuplicate = 1 if countData.isDuplicate else 0
                s += (
                    f"\n{flight}\t{airframe}\t{transect}\t{imageName}"
                    f"\t{countData.species}\t{countData.number}"
                    f"\t{isDuplicate}\t{countData.notes}\t{config.username}"
                )
        return s

    def allImages(self) -> list:
        """
        Returns a list of all the image names.
        """
        imageNames = []
        for dataGroup in self.data:
            imageNames.extend(dataGroup.saveData.uniqueImages())
        return imageNames

    def animalsAt(self, idx: int) -> str:
        """
        Returns a string describing ALL the animals found in
        each image at the particular index.
        """
        imageNames = self.allImages()

        try:
            targetImage = imageNames[idx]
        except IndexError:
            return f"Error: Image at index {idx} could not be found"

        s = f"{targetImage}:"

        for dataGroup in self.data:
            for imageName, countData in dataGroup.saveData.imageCounts():
                if imageName == targetImage:
                    # This is the image, make the string to display!
                    s += f"\n   - {countData.number} {countData.species}"
                    if countData.isDuplicate:
                        s += " (already counted)"

        return s

    def summaryAt(self, idx: int) -> str:
        """
        Returns a summary of the animals found at a particular item
        in the `groupedDict()`
        """
        groupName, saveDatas = list(self.groupedDict().items())[idx]
        s = f"{groupName}:"
        s += f"\n   - {saveDatas.numSpecies()} species"
        s += f"\n   - {saveDatas.numUniqueAnimals()} unique animals"
        s += f"\n   - {len(saveDatas.allImages())} images with animals"
        return s

    def numSpecies(self):
        num = 0
        for dataGroup in self.data:
            num += len(dataGroup.saveData.uniqueSpecies())
        return num

    def numUniqueAnimals(self):
        num = 0
        for dataGroup in self.data:
            num += len(dataGroup.saveData.uniqueAnimals())
        return num

    def sorted(self):
        # First sort each internal structure
        for dataGroup in self.data:
            dataGroup.saveData = dataGroup.saveData.sorted()

        # Sort the overall list
        return TransectDataGroupList(sorted(self, key=lambda dg: dg.name))

    def numImages(self):
        """ The number of images in the save data """
        num = 0
        for dataGroup in self.data:
            num += len(dataGroup.saveData.uniqueImages())
        return num

    def groupedDict(self):
        """
        Create an ordered dictionary of the save groups.
        OrderedDict(
            ('GroupName', TransectDataGroupList()),
            ('GroupName2', TransectDataGroupList()),
        )
        """
        # For optimization purposes, only generate this dictionary once.
        if self._groupedDict is not None:
            return self._groupedDict

        d = OrderedDict()
        for dataGroup in self.data:

            # Only include save files that have at least one count,
            # not just a drawing.
            if len(dataGroup.saveData.uniqueImages()) == 0:
                continue

            # Create a dictionary of `TransectDataGroupList` that
            # are keyed by the group name.
            try:
                d[dataGroup.name]
            except KeyError:
                d[dataGroup.name] = TransectDataGroupList([dataGroup])
            else:
                d[dataGroup.name].append(dataGroup)
        return d

    def isGrouped(self):
        numGroups = len(self.groupedDict())
        if numGroups == 1:
            return False
        else:
            return True

    def numGroups(self):
        """
        The number of discrete groups in this set of save data
        """
        return len(self.groupedDict())

    def indexOfGroupName(self, name):
        """
        The index of the first TransectDataGroup with a matching `name`.
        If the name cannot be found, `None` is returned.
        """
        for i, groupName in enumerate(self.groupedDict().keys()):
            if groupName == name:
                return i
        return None

    def indexOfImageName(self, name):
        """
        The index of the first image with a matching `name`.
        """
        try:
            return self.allImages().index(name)
        except ValueError:
            return None
