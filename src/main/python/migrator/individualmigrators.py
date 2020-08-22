import json

from base import config
from transectdata import GetSaveFiles


class IndividualMigrators:
    def migrate0_3_0(self):
        """Change saved CountData() to <i>not</i> be a
        string and instead be saved as a JSON dictionary
        """
        libraryDir = config.libraryDirectory
        saveFiles = GetSaveFiles(libraryDir)

        # For each save file, load it with the old JSON serializer
        # and write it back with the new one
        for saveFileTuple in saveFiles:
            savePath = saveFileTuple[1]

            with open(savePath, "r") as f:
                data = json.load(f)

            upgradedData = {}

            for key, value in data.items():
                try:
                    drawingString = value["drawings"]
                except KeyError:
                    pass
                else:
                    # Replace the drawings with it's un-serialized counterpart
                    if isinstance(drawingString, str):
                        drawings = json.loads(drawingString)

                        # Replace any "null" count data with a default implementation
                        for drawing in drawings:
                            if drawing["CountData"] is None:
                                drawing["CountData"] = {
                                    "Species": "",
                                    "Number": 1,
                                    "isDuplicate": False,
                                    "Notes": "",
                                }

                        # Replace drawings string with an actual object
                        value["drawings"] = drawings
                finally:
                    upgradedData[key] = value

            # Overwrite save data with upgraded data, include pretty indents
            with open(savePath, "w") as f:
                json.dump(upgradedData, f, indent=4)
