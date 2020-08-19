import json
from pathlib import Path
from typing import Dict

from countdata import CountData
from drawingdata import DrawingDataList


class TransectData:
    """
    Manages transect save data in a primitive
    data state, such that it can be easily
    serialized.
    """

    def __init__(self, transectData: Dict[str, Dict[str, list]], fp: Path):
        """
        {
            'ImageName.jpg':
            {
                "drawings":
                [
                    DrawingData1.toDict(),
                    DrawingData2.toDict(),
                    ...
                ]
            }
        }

        Include `fp` for traceability.
        """
        self._transectData: Dict[str, Dict[str, list]] = transectData
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
            print(
                f"Badly formed JSON file. Data will be overwritten when file is saved: {fp}"
            )
            data = {}

        return TransectData(data, fp)

    def dump(self, fp):
        """
        Serialize save data and save to specified path.
        Writes this data on top of already existing data.
        """
        with open(fp, "w") as f:
            json.dump(self._transectData, f, indent=4)

    def addImage(self, imageName):
        """
        Ensure that an image with the name
        imageName is in this save data.
        """
        if imageName not in self._transectData.keys():
            self._transectData[imageName] = {}

    def addDrawings(self, imageName, drawings: DrawingDataList):
        """
        Add drawings (for a specific image) to the
        save data. This will replace any drawings currently
        in this save data instance associated with this
        image.
        """

        # Ensure image name is present
        self.addImage(imageName)

        # Add these drawings the image dict
        self._transectData[imageName]["drawings"] = drawings.toDict()

    def removeDrawings(self, imageName: str):
        """
        Remove the drawings associated with an image.
        """
        if imageName in self._transectData.keys():
            try:
                self._transectData[imageName].pop("drawings")

            # There might not have been this data saved yet
            except KeyError:
                pass

    def imageHasDrawings(self, imageName: str, otherDrawings: DrawingDataList):
        """
        Compares the drawings associated with `imageName`,
        and returns `True` if those drawings match `otherDrawings`.
        """

        # Check if image has no drawings or data
        if imageName not in self._transectData.keys():
            return False

        # Check if image has no drawings
        if "drawings" not in self._transectData[imageName].keys():
            return False

        # Check if image drawings are the same as the input
        # also lol TODO stop this maddness
        drawings = DrawingDataList.loads(
            json.dumps(self._transectData[imageName]["drawings"])
        )
        return drawings == otherDrawings

    def drawings(self):
        """
        Generator yielding a tuple of images
        with corresponding drawings.
        (imageName:str, drawings:DrawingDataList)
        """
        for imageName, imageData in self._transectData.items():
            if "drawings" in imageData.keys():
                yield imageName, DrawingDataList.load(imageData["drawings"])

    def imageCounts(self):
        """
        Generator yielding tuple of images
        and their counts.
        (imageName:str, counts:CountData)
        """
        for imageName, imageData in self._transectData.items():
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

    def __repr__(self):
        return f"TransectData({super().__repr__()})"

    def sorted(self):
        """Sort by key values (image names)"""
        return TransectData(
            dict(sorted(self._transectData.items(), key=lambda t: t[0])), self.fp
        )
