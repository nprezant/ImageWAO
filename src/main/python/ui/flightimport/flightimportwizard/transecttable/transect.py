import os


class Transect:
    def __init__(self, name=None, files=None):
        self.name = name if name is not None else "Transect"
        self.files = files if files is not None else []

    @property
    def numFiles(self):
        return len(self.files)

    @property
    def firstLastText(self):
        first = self.files[0]
        last = self.files[-1]
        return f"{os.path.basename(first)} . . . {os.path.basename(last)}"

    def addFile(self, fp):
        self.files.append(fp)

    def clearFiles(self):
        self.files.clear()
