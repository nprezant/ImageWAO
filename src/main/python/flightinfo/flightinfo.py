from pathlib import Path
import json


class FlightInfo:
    def __init__(self, airframe: str, date: str, time: str, notes: str):
        self.airframe = airframe
        self.date = date
        self.time = time
        self.notes = notes

    @staticmethod
    def readInfoFile(infoFile: Path):
        with open(infoFile, "r") as f:
            saveData: dict = json.load(f)

        expectedKeys = ["Airframe", "FlightDate", "FlightTime", "FlightNotes"]
        for key in expectedKeys:
            if key not in saveData.keys():
                raise KeyError(
                    f"Expected key '{key}' in flight info file '{infoFile}''"
                )

        return FlightInfo(
            saveData["Airframe"],
            saveData["FlightDate"],
            saveData["FlightTime"],
            saveData["FlightNotes"],
        )

    def writeInfoFile(self, infoFile: Path):
        infoData = {
            "Airframe": self.airframe,
            "FlightDate": self.date,
            "FlightTime": self.time,
            "FlightNotes": self.notes,
        }
        infoFile.touch(exist_ok=True)
        with open(infoFile, "w") as f:
            json.dump(infoData, f, indent=4)
