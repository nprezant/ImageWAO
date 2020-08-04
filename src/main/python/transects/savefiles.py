import os
from typing import List, Tuple
from pathlib import Path

from base import config


def fast_scandir(dirname) -> List[os.DirEntry]:
    """
    Quickly scans all subfolders recursively.
    Faster than `os.walk` and much faster than `glob`.
    Returns list of os.DirEntry() objects.
    """
    subfolders = [f for f in os.scandir(dirname) if f.is_dir()]
    for dirname in list(subfolders):
        subfolders.extend(fast_scandir(dirname))
    return subfolders


def GetSaveFiles(folder: Path) -> List[Tuple[str, Path]]:
    """ Finds all save files recursively, grouped by the
    subfolder relative to the `folder` input.

    Returns a list of tuples joining each save file with the
    subfolder it belongs to.
        [
            (subfolder1name, path/to/save/file/1/in/sub/1)
            (subfolder1name, path/to/save/file/2/in/sub/1)
            (subfolder2name, path/to/save/file/1/in/sub/2)
            (subfolder2name, path/to/save/file/2/in/sub/2)
        ]
    """
    markedFolderMatchString = config.markedImageFolderName
    subfolders = [f for f in os.scandir(folder) if f.is_dir()]
    saveFiles = []
    for dirname in list(subfolders):
        allfolders = fast_scandir(dirname)
        markedFolders = [d for d in allfolders if d.name == markedFolderMatchString]
        for markedFolder in markedFolders:
            saveFile = config.markedDataFile(transectFolder=Path(markedFolder).parent)
            if saveFile.exists():
                saveFiles.append((dirname.name, saveFile))
    return saveFiles
