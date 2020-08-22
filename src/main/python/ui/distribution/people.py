import json
from pathlib import Path
from typing import List

from .person import Person


class People:
    def __init__(self, people: List[Person]):
        self.people = people

    def dump(self, fp: Path):
        dumpable = []
        for person in self.people:
            dumpable.append(person.toDict())
        with open(fp, "w") as f:
            json.dump(dumpable, f, indent=4)

    @staticmethod
    def loadFromFile(fp: Path) -> List[Person]:
        with open(fp, "r") as f:
            rawList = json.load(f)
        if not isinstance(rawList, list):
            raise json.JSONDecodeError(
                "Expected top level of distribution file to be a list", fp.name, 1
            )

        people: List[Person] = []
        for rawPerson in rawList:
            people.append(Person.fromDict(rawPerson))

        return people
