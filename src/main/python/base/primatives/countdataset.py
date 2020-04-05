
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

    def addData(self, key:str, data:CountData):
        ''' Adds count data to this set. '''

        speciesKey = data.species
        if data.isDuplicate:
            speciesKey += ' (duplicate)'

        try:
            self[key]
        except KeyError:
            self[key] = {speciesKey: data}
        else:
            dataSet = self[key]
            try:
                dataSet[speciesKey]
            except KeyError:
                dataSet[speciesKey] = data
            else:
                dataSet[speciesKey] += data

    def displayIndex(self, idx:int):
        '''Displays the data at the given index nicely.'''
        key, dataSet = list(self.items())[idx]
        s = key
        for speciesKey, data in dataSet.items():
            s += f'\n    - {data.number} {speciesKey}'
        return s

    def __iadd__(self, other):
        for key, dataSet in other.items():
            for countData in dataSet.values():
                self.addData(key, countData)
        return self

