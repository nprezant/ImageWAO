
import json
from collections import UserDict

from base.primatives import CountData, CountDataSet


class TransectSaveData(UserDict):
    '''
    Manages transect save data in a primitive
    data state, such that it can be easily 
    serialized.
    '''

    def __init__(self, data={}):
        super().__init__(data)

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
            data = {}

        return TransectSaveData(data)

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
