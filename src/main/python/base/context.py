from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide2 import ApplicationContext

from PySide2 import QtGui


class AppContext(ApplicationContext):
    """
    Low level class for holding the application context.
    This class must be used to get application resources,
    using the `get_resource` method.
    It can be convenient to store commonly used images as
    a cached_property in this class.
    """

    def version(self):
        return self.build_settings["version"]

    def icon(self, fp):
        """
        Convenience method for returning an icon
        of the image at the given path, `fp`.
        """
        return QtGui.QIcon(self.get_resource(fp))

    def pixmap(self, fp):
        """
        Convenience method for returning a pixmap
        of the image at the given path, `fp`.
        """
        return QtGui.QPixmap(self.get_resource(fp))

    @cached_property
    def defaultDockIcon(self):
        return QtGui.QIcon(self.get_resource("icons/storage.png"))

    @cached_property
    def closeDockIcon(self):
        return QtGui.QIcon(self.get_resource("icons/close.png"))

    @cached_property
    def explorerIcon(self):
        return QtGui.QIcon(self.get_resource("icons/explorer.png"))

    @cached_property
    def loadingAnimalsPixmap(self):
        return QtGui.QPixmap(self.get_resource("images/loadingAnimals.png"))


context = AppContext()
