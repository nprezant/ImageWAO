
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

    _duplicationNote = ' (duplicate)'

    def addData(self, key:str, data:CountData):
        ''' Adds count data to this set. '''

        speciesKey = data.species
        if data.isDuplicate:
            speciesKey += self._duplicationNote

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

    def animalsAt(self, idx:int) -> str:
        '''
        Displays a list of the animals and their counts
        at the given index in a nice, printable `str` format.
        '''
        key, dataSet = list(self.items())[idx]
        s = key
        for speciesKey, data in dataSet.items():
            s += f'\n    - {data.number} {speciesKey}'
        return s

    def summaryAt(self, idx:int) -> str:
        '''
        Displays a summary of the animals counted at this index
        in a printable `str` format
        '''
        key, dataSet = list(self.items())[idx]
        uniqueAnimalsCounted = 0
        uniqueSpeciesCounted = 0
        for _, data in dataSet.items():
            if not data.isDuplicate:
                uniqueAnimalsCounted += data.number
                uniqueSpeciesCounted += 1

        s = key
        s += f'\n    - {uniqueSpeciesCounted} species'
        s += f'\n    - {uniqueAnimalsCounted} unique animals'
        return s

    def clipboardText(self):
        '''
        Returns text containing all identifying data, copyable to the clipboard.
        '''
        s = 'Top Level\tSpecies\tNumber\tIs Duplicate\tNotes'
        for topLevel, dataSet in self.items():
            for speciesKey, countData in dataSet.items():
                s += f'\n{topLevel}\t{speciesKey}\t{countData.number}\t{countData.isDuplicate}\t{countData.notes}'
        return s

    def __iadd__(self, other):
        for key, dataSet in other.items():
            for countData in dataSet.values():
                self.addData(key, countData)
        return self

