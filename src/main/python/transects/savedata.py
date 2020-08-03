import json
from collections import UserDict

from base.primatives import CountData, CountDataSet
from serializers import JSONDrawnItems


class TransectSaveData(UserDict):
    """
    Manages transect save data in a primitive
    data state, such that it can be easily
    serialized.
    """

    def __init__(self, data, fp):
        """
        A UserDict. Include `fp` for traceability.
        """
        super().__init__(data)
        self.fp = fp

    @staticmethod
    def load(fp):
        """
        Loads a serialized file. If the data cannot be decoded,
        The save data is initialized with a blank dict.
        """
        try:
            with open(fp, "r") as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            print(f"Badly formed JSON file: {fp}")
            data = {}

        # Legacy -- if drawings are stored as a string, upgrade them
        # TODO fix this
        return TransectSaveData(data, fp)

    def dump(self, fp):
        """
        Serialize save data and save to specified path.
        Writes this data on top of already existing data.
        """
        with open(fp, "w") as f:
            json.dump(self.data, f, indent=4)

    def addImage(self, imageName):
        """
        Ensure that an image with the name
        imageName is in this save data.
        """
        if imageName not in self.data.keys():
            self.data[imageName] = {}

    def addDrawings(self, imageName, drawings: JSONDrawnItems):
        """
        Add drawings (for a specific image) to the
        save data. This will replace any drawings currently
        in this save data instance associated with this
        image.
        """

        # Ensure image name is present
        self.addImage(imageName)

        # Add these drawings the image dict
        self.data[imageName]["drawings"] = drawings

    def removeDrawings(self, imageName: str):
        """
        Remove the drawings associated with an image.
        """
        if imageName in self.data.keys():
            try:
                self.data[imageName].pop("drawings")

            # There might not have been this data saved yet
            except KeyError:
                pass

    def imageHasDrawings(self, imageName: str, otherDrawings: JSONDrawnItems):
        """
        Compares the drawings associated with `imageName`,
        and returns `True` if those drawings match `otherDrawings`.
        """

        # Check if image has no drawings or data
        if imageName not in self.data.keys():
            return False

        # Check if image has no drawings
        if "drawings" not in self.data[imageName].keys():
            return False

        # Check if image drawings are the same as the input
        # also lol TODO stop this maddness
        drawings = JSONDrawnItems.loads(json.dumps(self.data[imageName]["drawings"]))
        return drawings == otherDrawings

    def drawings(self):
        """
        Generator yielding a tuple of images
        with corresponding drawings.
        (imageName:str, drawings:str)
        """
        for imageName, imageData in self.data.items():
            if "drawings" in imageData.keys():
                yield imageName, imageData["drawings"]

    def imageCounts(self):
        """
        Generator yielding tuple of images
        and their counts.
        (imageName:str, counts:CountData)
        """
        for imageName, imageData in self.data.items():
            if "drawings" in imageData.keys():
                drawings = imageData["drawings"]
                for drawing in drawings:
                    countData = CountData.fromDict(drawing["CountData"])
                    if not countData.isEmpty():
                        yield imageName, countData

    def uniqueSpecies(self):
        """
        Returns a list of all the different species in this save file
        """
        species = []
        for _, countData in self.imageCounts():
            if countData.species not in species:
                species.append(countData.species)
        return species

    def uniqueAnimals(self):
        """
        Returns a list of the animals in this data set, excluding those
        marked as "duplicates". The length of this list is the total number of animals counted
        in this data set.
        """
        animals = []
        for _, countData in self.imageCounts():
            if not countData.isDuplicate:
                animals.extend([countData.species] * countData.number)
        return animals

    def uniqueImages(self):
        """
        Returns a list of unique images in this data set.
        """
        imageNames = []
        for imageName, _ in self.imageCounts():
            if imageName not in imageNames:
                imageNames.append(imageName)
        return imageNames

    def countDataSet(self, topLevel=None):
        """
        Computes the count data set from this save data.

        If the `topLevel` is not specified, the data set will
        be categorized with respect to the image name.
        If the `topLevel` is given, all counts will be categorized
        with respect to that `topLevel`.
        """
        countSet = CountDataSet()
        for imageName, countData in self.imageCounts():
            if topLevel is not None:
                countSet.addData(topLevel, countData)
            else:
                countSet.addData(imageName, countData)
        return countSet

    def __repr__(self):
        return f"TransectSaveData({super().__repr__()}"

    def sorted(self):
        return TransectSaveData(sorted(self.items(), key=lambda t: t[0]), self.fp)
