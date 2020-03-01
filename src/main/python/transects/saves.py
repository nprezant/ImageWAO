
import json
from collections import UserDict

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
        Loads a serialized file
        '''
        with open(fp, 'r') as f:
            data = json.load(f)

        return TransectSaveData(data)

    def dump(self, fp):
        '''
        Serialize save data and save to specified path.
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

    def drawings(self):
        '''
        Generator yielding a tuple of images
        with corresponding drawings.
        (imageName:str, drawings:str)
        '''
        for imageName, imageData in self.data.items():
            if 'drawings' in imageData.keys():
                yield imageName, imageData['drawings']
