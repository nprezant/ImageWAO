"""
This file provides a class for handling, serializing, reading, and writing animal count data.
"""


class CountData:
    def __init__(
        self,
        species: str = "",
        number: int = 1,
        isDuplicate: bool = False,
        notes: str = "",
    ):
        self.species = species
        self.number = number
        self.isDuplicate = isDuplicate
        self.notes = notes

    def toDict(self):
        """
        Converts this class to an easily serializable dict.
        """
        return {
            "Species": self.species,
            "Number": self.number,
            "isDuplicate": self.isDuplicate,
            "Notes": self.notes,
        }

    @staticmethod
    def fromDict(d: dict):
        """
        Initializes object from a dict. Ideally created with `toDict` method.
        If the input dict is empty, return a blank initialized CountData.
        """

        if d in ({}, None):  # None included for legacy compatibility
            return CountData()

        # Retreive values
        species = d["Species"]
        number = d["Number"]
        isDuplicate = d["isDuplicate"]
        notes = d["Notes"]

        # Create instance
        return CountData(species, number, isDuplicate, notes)

    def toToolTip(self):
        """
        Converts the data in this object into a string suitable for a tool tip.
        """
        s = f"{self.number} {self.species}"
        if self.isDuplicate:
            s += " (already counted)"
        if self.notes:
            s += f"\n{self.notes}"
        return s

    def isEmpty(self):
        """
        Tests whether this count data contains any information
        that differs from the default.
        """
        return self == CountData()

    def __eq__(self, other):
        return (
            self.species == other.species
            and self.number == other.number
            and self.isDuplicate == other.isDuplicate
            and self.notes == other.notes
        )

    def __repr__(self):
        noBreakNotes = self.notes.replace("\n", "")
        return f'CountData({self.species}, {self.number}, isDuplicate:{self.isDuplicate}, notes:"{noBreakNotes}")'

    def __iadd__(self, other):
        """ Implement `+=` functionality. """
        if self.species != other.species:
            raise ValueError(
                "Cannot add in place when species "
                f"do not match: {self.species}; {other.species}"
            )

        if self.isDuplicate != other.isDuplicate:
            raise ValueError("Cannot add in place when isDuplicate does not match")

        self.number += other.number
        self.notes += other.notes
        return self
