import os
from pathlib import Path

from PySide2 import QtCore, QtWidgets, QtGui

from .pages import (
    PageIds,
    IntroPage,
    ParametersPage,
    ReviewPage,
    MetadataPage,
    SetLibraryPage,
    ConclusionPage,
)


class FlightImportWizard(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()

        # Look and feel
        # this page should not have a cancel button
        self.setOption(QtWidgets.QWizard.NoCancelButton)

        # page instances
        introPage = IntroPage(self)
        parametersPage = ParametersPage(self)
        reviewPage = ReviewPage(self)
        metadataPage = MetadataPage(self)
        setLibraryPage = SetLibraryPage(self)
        conclusionPage = ConclusionPage(self)

        # connections
        reviewPage.modelChanged.connect(conclusionPage.updateModel)

        # set page numbers
        self.setPage(PageIds.Page_Intro, introPage)
        self.setPage(PageIds.Page_Parameters, parametersPage)
        self.setPage(PageIds.Page_Review, reviewPage)
        self.setPage(PageIds.Page_Metadata, metadataPage)
        self.setPage(PageIds.Page_SetLibrary, setLibraryPage)
        self.setPage(PageIds.Page_Conclusion, conclusionPage)

        self.setWindowTitle("Flight Import Wizard")

        # connect next button to save page defaults if applicable
        self.button(self.NextButton).clicked.connect(self._saveCurrentPageDefaults)

    def _saveCurrentPageDefaults(self):
        try:
            # have to get the PREVIOUS page
            self.page(self.visitedPages()[-2])._saveDefaults()
        except AttributeError:
            pass

    @staticmethod
    def openNew():
        """
        Creates and opens a new FlightImportWizard using the `exec_` method.
        """
        FlightImportWizard().exec_()
