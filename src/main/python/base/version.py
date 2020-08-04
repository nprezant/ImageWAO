class Version:
    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    @staticmethod
    def fromString(s: str):
        parts = s.split(".")
        if len(parts) != 3:
            raise ValueError(f"Version string must have 3 parts: {s}")

        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])

        return Version(major, minor, patch)

    def toString(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other):
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __lt__(self, other):
        if self.major < other.major:
            return True

        elif self.major == other.major:
            if self.minor < other.minor:
                return True

            elif self.minor == other.minor:
                if self.patch < other.patch:
                    return True

        return False

    def __gt__(self, other):
        if self == other or self < other:
            return False
        else:
            return True

    def __repr__(self):
        return f"Version('{self.toString()}')"
