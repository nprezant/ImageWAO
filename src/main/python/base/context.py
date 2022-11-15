from functools import cached_property

from PySide6 import QtGui, QtWidgets

import os
import errno


class ResourceLocator:
    def __init__(self, resource_dirs):
        self._dirs = resource_dirs

    def locate(self, *rel_path):
        for resource_dir in self._dirs:
            resource_path = os.path.join(resource_dir, *rel_path)
            if os.path.exists(resource_path):
                return os.path.realpath(resource_path)
        raise FileNotFoundError(
            errno.ENOENT, 'Could not locate resource', os.sep.join(rel_path)
        )


class AppContext:
    """
    Low level class for holding the application context.
    This class must be used to get application resources,
    using the `get_resource` method.
    It can be convenient to store commonly used images as
    a cached_property in this class.
    """

    def __init__(self):
        self.app
        self._resources = ResourceLocator(["/home/noah/projects/ImageWAO/src/main/resources/base"])

    def version(self):
        return "0.3.0" # TODO this should pull from the settings file

    def get_resource(self, fp):
        return self._resources.locate(fp)

    @cached_property
    def app(self):
        """
        The global Qt QApplication object for your app. Feel free to overwrite
        this property, eg. if you wish to use your own subclass of QApplication.
        An example of this is given in the Manual.
        """
        result = QtWidgets.QApplication([])
        result.setApplicationName("ImageWAO")
        result.setApplicationVersion("0.3.0")
        return result

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
