
import json

class TransectSaveData:
    '''
    Manages transect save data in a primitive
    data state, such that it can be easily 
    serialized.
    '''

    def __init__(self):
        self.data = {}

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

    def dump(self, fp):
        '''
        Serialize save data and save to specified path.
        '''
        json.dump(self.data, fp)

    
