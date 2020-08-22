from .transectdata import TransectData


class TransectDataGroup:
    def __init__(self, name, saveData):
        self.name: str = name
        self.saveData: TransectData = saveData
