from PySide2 import QtCore


class TitleBarText(QtCore.QObject):
    """
    Manages the title bar text.
    Connect the changed signal to a slot
    that updates the title bar text, then
    simply set the TitleBarText properties
    to update the title bar.
    """

    # Text signal emitted when title bar is changed
    changed = QtCore.Signal(str)

    def __init__(self, appName):
        super().__init__()
        self.appName = appName
        self._dirty = False
        self._folderName = None
        self._text = ""

    def setDirty(self, value):
        """
        A flag will be shown in the title bar
        Denoting that the application has unsaved
        changes
        """
        self._dirty = value
        self._makeText()

    def setFolderName(self, value):
        """
        str() property will be displayed in text.
        Set to None to remove from title bar. """
        self._folderName = value
        self._makeText()

    def _makeText(self):
        """
        Combines text together based on internal
        properties to generate the titlebar text.
        Emits this with the changed() signal.
        """
        if self._dirty:
            prefix = "* "
        else:
            prefix = ""

        if self._folderName is not None:
            folderName = f" - {self._folderName}"
        else:
            folderName = ""

        self._text = f"{prefix}{self.appName}{folderName}"
        self.changed.emit(self._text)
