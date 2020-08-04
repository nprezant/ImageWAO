class Transect:
    def __init__(self, name="Transect", files=[]):
        self.name = name
        self.files = files

    @property
    def numFiles(self):
        return len(self.files)

    @property
    def firstLastText(self):
        first = self.files[0]
        last = self.files[-1]
        return f"{first.name} . . . {last.name}"

    def addFile(self, fp):
        self.files.append(fp)

    def clearFiles(self):
        self.files.clear()
