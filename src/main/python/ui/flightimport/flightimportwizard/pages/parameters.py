from PySide6 import QtWidgets

from base import config

from .ids import PageIds


class ParametersPage(QtWidgets.QWizardPage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTitle("Sorting Algorithm Parameters")
        self.setSubTitle(
            "<b>You probably don't need to change these.</b><br/>"
            "These parameters govern the algorithm that categorizes "
            "flight photos into transects. "
            "Hover over the descriptions for more information. "
        )

        # photo delay
        self.maxDelayLabel = QtWidgets.QLabel("Max time between photos")
        self.maxDelayLabel.setToolTip(
            "Maximum number of seconds between "
            "photos on the same transect.\n\n"
            "This will be used to determine where one transect "
            "ends and another begins."
        )
        self.maxDelayBox = QtWidgets.QSpinBox()
        self.maxDelayBox.setRange(1, 1000)
        self.maxDelayBox.setSuffix(" seconds")
        self.maxDelayBox.setToolTip(self.maxDelayLabel.toolTip())
        self.registerField("maxDelay", self.maxDelayBox)

        # min transect photo count
        self.minCountLabel = QtWidgets.QLabel("Min photos per transect")
        self.minCountLabel.setToolTip(
            "Minimum number of photos expected on the same transect.\n\n"
            "This number will be used to rule out one-off test images."
        )
        self.minCountBox = QtWidgets.QSpinBox()
        self.minCountBox.setRange(1, 1000)
        self.minCountBox.setSuffix(" photos")
        self.minCountBox.setToolTip(self.minCountLabel.toolTip())
        self.registerField("minCount", self.minCountBox)

        layout = QtWidgets.QFormLayout()
        layout.addRow(self.maxDelayLabel, self.maxDelayBox)
        layout.addRow(self.minCountLabel, self.minCountBox)
        self.setLayout(layout)

    def initializePage(self):
        maxDelay = config.maxPhotoDelay
        minCount = config.minPhotosPerTransect
        self.maxDelayBox.setValue(int(maxDelay))
        self.minCountBox.setValue(int(minCount))

    def _saveDefaults(self):
        config.maxPhotoDelay = self.maxDelayBox.value()
        config.minPhotosPerTransect = self.minCountBox.value()

    def nextId(self):
        return PageIds.Page_Review
