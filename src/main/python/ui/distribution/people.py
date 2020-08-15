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
