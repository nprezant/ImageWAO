
class Config:

    def __init__(self):

        # Files and folders in the "Flight" directory.
        # E.g. Flight01/.flight/meta.json
        self.flightDataFolder = '.flight/'
        self.flightMetaFile = '.flight/meta.json'
        self.flightDistributionFile = '.flight/distribution.json'

        # Files and folders in each transect directory
        self.markedImageFolder = '.marked/'
        self.transectDataFolder = '.transect/'
        self.transectCountFile = '.transect/counts.json'

        # Drawing colors
        self.colors = [
            '#3296e6', # Teleric Blue
            'Blue',
            'DarkGreen',
            'Teal',
            'Red',
            'Orange',
            'Magenta',
            'Black',
            'White',
        ]

config = Config()
