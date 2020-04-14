
import json
from enum import Enum
from pathlib import Path
from collections import UserDict, UserList, OrderedDict

from base import config
from base.primatives import CountData, CountDataSet


class TransectSaveData(UserDict):
    '''
    Manages transect save data in a primitive
    data state, such that it can be easily 
    serialized.
    '''

    def __init__(self, data={}, fp=None):
        '''
        A UserDict. Optionally include `fp` for traceability.
        '''
        super().__init__(data)
        self.fp = fp

    @staticmethod
    def load(fp):
        '''
        Loads a serialized file. If the data cannot be decoded,
        The save data is initialized with a blank dict.
        '''
        try:
            with open(fp, 'r') as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError:
            print(f'Badly formed JSON file: {fp}')
            data = {}

        return TransectSaveData(data, fp)

    def dump(self, fp):
        '''
        Serialize save data and save to specified path.
        Writes this data on top of already existing data.
        '''
        with open(fp, 'w') as f:
            json.dump(self.data, f)

    def addImage(self, imageName):
        '''
        Ensure that an image with the name
        imageName is in this save data.
        '''
        if not imageName in self.data.keys():
            self.data[imageName] = {}

    def addDrawings(self, imageName, drawings:str):
        '''
        Add drawings (for a specific image) to the
        save data. This will replace any drawings currently
        in this save data instance associated with this
        image.
        '''
        
        # Ensure image name is present
        self.addImage(imageName)

        # Add these drawings the image dict
        self.data[imageName]['drawings'] = drawings

    def removeDrawings(self, imageName):
        '''
        Remove the drawings associated with an image.
        '''
        if imageName in self.data.keys():
            try:
                self.data[imageName].pop('drawings')

            # There might not have been this data saved yet
            except KeyError:
                pass

    def imageHasDrawings(self, imageName:str, otherDrawings:str):
        '''
        Compares the drawings associated with `imageName`,
        and returns `True` if those drawings match `otherDrawings`.
        '''
        if imageName in self.data.keys():
            try:
                drawings = self.data[imageName]['drawings']

            # There might not be any drawings currently here
            except KeyError:
                drawings = '[]'

            finally:
                return drawings == otherDrawings

    def drawings(self):
        '''
        Generator yielding a tuple of images
        with corresponding drawings.
        (imageName:str, drawings:str)
        '''
        for imageName, imageData in self.data.items():
            if 'drawings' in imageData.keys():
                yield imageName, imageData['drawings']

    def imageCounts(self):
        '''
        Generator yielding tuple of images
        and their counts.
        (imageName:str, counts:CountData)
        '''
        for imageName, imageData in self.data.items():
            if 'drawings' in imageData.keys():
                drawings = json.loads(imageData['drawings'])
                for drawing in drawings:
                    if drawing['CountData'] is not None:
                        yield imageName, CountData.fromDict(drawing['CountData'])

    def uniqueSpecies(self):
        '''
        Returns a list of all the different species in this save file
        '''
        species = []
        for _, countData in self.imageCounts():
            if not countData.species in species:
                species.append(countData.species)
        return species

    def uniqueAnimals(self):
        '''
        Returns a list of the animals in this data set, excluding those
        marked as "duplicates". The length of this list is the total number of animals counted
        in this data set.
        '''
        animals = []
        for _, countData in self.imageCounts():
            if not countData.isDuplicate:
                animals.extend([countData.species]*countData.number)
        return animals

    def uniqueImages(self):
        '''
        Returns a list of unique images in this data set.
        '''
        imageNames = []
        for imageName, _ in self.imageCounts():
            if not imageName in imageNames:
                imageNames.append(imageName)
        return imageNames

    def countDataSet(self, topLevel=None):
        '''
        Computes the count data set from this save data.

        If the `topLevel` is not specified, the data set will
        be categorized with respect to the image name.
        If the `topLevel` is given, all counts will be categorized
        with respect to that `topLevel`.
        '''
        countSet = CountDataSet()
        for imageName, countData in self.imageCounts():
            if topLevel is not None:
                countSet.addData(topLevel, countData)
            else:
                countSet.addData(imageName, countData)
        return countSet

    def __repr__(self):
        return f'TransectSaveData({super().__repr__()}'

    def sorted(self):
        return TransectSaveData(sorted(self.items(), key=lambda t: t[0]))


class ReportLevel(Enum):
    PerImage = 1
    PerTransect = 2
    PerFlight = 3


class SaveDataGroup:
    def __init__(self, name, saveData):
        self.name = name
        self.saveData = saveData


class TransectSaveDatas(UserList):
    '''
    This class manages multiple transect save files and
    provides easy access methods for displaying and 
    summarizing the data.

    `data` is a list of `TransectSaveData`
    '''

    def load(self, fp, groupName=None):
        '''
        Loads a save file into this collection of save files.
        Specify the `groupName` if you want to group the save
        data any particular way.
        '''
        self.data.append(
            SaveDataGroup(groupName, TransectSaveData.load(fp)))

    def clipboardText(self):
        '''
        Returns a string that can be copied and pasted into excel/notepad
        '''
        s = 'Flight\tTransect\tImage\tSpecies\tNumber\tIsDuplicate\tNotes'
        for saveGroup in self.data:
            rel = saveGroup.saveData.fp.relative_to(config.defaultLibraryDirectory)
            flight = rel.parts[0]
            transect= rel.parts[1]
            for imageName, countData in saveGroup.saveData.imageCounts():
                isDuplicate = 1 if countData.isDuplicate else 0
                s += (
                    f'\n{flight}\t{transect}\t{imageName}'
                    f'\t{countData.species}\t{countData.number}'
                    f'\t{isDuplicate}\t{countData.notes}')
        return s

    def allImages(self) -> list:
        '''
        Returns a list of all the image names.
        '''
        imageNames = []
        for dataGroup in self.data:
            imageNames.extend(dataGroup.saveData.uniqueImages())
        return imageNames

    def animalsAt(self, idx:int) -> str:
        '''
        Returns a string describing ALL the animals found in
        each image at the particular index.
        '''
        imageNames = self.allImages()

        try:
            targetImage = imageNames[idx]
        except IndexError:
            return f'Error: Image at index {idx} could not be found'

        s = f'{targetImage}:'

        for dataGroup in self.data:
            for imageName, countData in dataGroup.saveData.imageCounts():
                if imageName == targetImage:
                    # This is the image, make the string to display!
                    s += f'\n   - {countData.number} {countData.species}'
                    if countData.isDuplicate:
                        s += f' (already counted)'
        
        return s

    def summaryAt(self, idx:int) -> str:
        '''
        Returns a summary of the animals found at a particular item
        in the `groupedDict()`
        '''
        groupName, saveDatas = list(self.groupedDict().items())[idx]
        s = f'{groupName}:'
        s += f'\n   - {saveDatas.numSpecies()} species'
        s += f'\n   - {saveDatas.numUniqueAnimals()} unique animals'
        s += f'\n   - {len(saveDatas.allImages())} images with animals'
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
        return TransectSaveDatas(sorted(self, key=lambda dg: dg.name))

    def numImages(self):
        ''' The number of images in the save data '''
        num = 0
        for dataGroup in self.data:
            num += len(dataGroup.saveData.uniqueImages())
        return num

    def groupedDict(self):
        '''
        Create an ordered dictionary of the save groups.
        OrderedDict(
            ('GroupName', TransectSaveDatas()),
            ('GroupName2', TransectSaveDatas()),
        )
        '''
        d = OrderedDict()
        for dataGroup in self.data:
            try:
                d[dataGroup.name]
            except KeyError:
                d[dataGroup.name] = TransectSaveDatas([dataGroup])
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
        '''
        The number of discrete groups in this set of save data
        '''
        return len(self.groupedDict())

    def indexOfGroupName(self, name):
        '''
        The index of the first SaveDataGroup with a matching `name`.
        If the name cannot be found, `None` is returned.
        '''
        for i, groupName in enumerate(self.groupedDict().keys()):
            if groupName == name:
                return i
        return None

    def indexOfImageName(self, name):
        '''
        The index of the first image with a matching `name`.
        '''
        try:
            return self.allImages().index(name)
        except ValueError:
            return None
