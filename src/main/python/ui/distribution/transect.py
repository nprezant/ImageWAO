from pathlib import Path
from typing import List


class Transect:
    def __init__(self, name: str, numPhotos: int):
        self.name = name
        self.numPhotos = numPhotos

    @staticmethod
    def createFromFlight(flightFolder: Path):
        """Returns List[Transect]"""
        transects: List[Transect] = []
        for transectDir in flightFolder.iterdir():
            if not (transectDir.is_file() or transectDir.name[0] == "."):
                photos = [fp for fp in transectDir.iterdir() if fp.is_file()]
                transects.append(Transect(transectDir.name, len(photos)))
        return transects
