
from collections import OrderedDict

from .countdata import CountData


class CountDataSet(OrderedDict):
    '''
    This class handles a set of count data.
    `CountData` can be added using `addData(key, data)`,
    and if the `key` already exists, the count data will
    simply be summed and flattened into one dataset.

    This is useful for summing the total number of animals
    in a single image, a single transect, a set of transects,
    etc.
    '''

    def addData(self, key:str, data:CountData, dropDuplicates=True):
        ''' Adds count data to this set. '''

        if dropDuplicates and data.isDuplicate:
            return

        try:
            self[key]
        except KeyError:
            self[key] = {data.species: data}
        else:
            dataSet = self[key]
            try:
                dataSet[data.species]
            except KeyError:
                dataSet[data.species] = data
            else:
                dataSet[data.species] += data

    def displayIndex(self, idx:int):
        '''Displays the data at the given index nicely.'''
        key, dataSet = list(self.items())[idx]
        s = key
        for data in dataSet.values():
            s += f'\n    - {data.number} {data.species}'
        return s

