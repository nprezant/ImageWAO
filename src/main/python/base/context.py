
from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context.PySide2 import ApplicationContext

from PySide2 import QtGui

class AppContext(ApplicationContext):
    '''
    Low level class for holding the application context.
    This class must be used to get application resources,
    using the `get_resource` method.
    It can be convenient to store commonly used images as
    a cached_property in this class.
    '''

    @cached_property
    def defaultDockIcon(self):
        return QtGui.QIcon(self.get_resource('icons/ic_storage.png'))

    @cached_property
    def closeDockIcon(self):
        return QtGui.QIcon(self.get_resource('icons/ic_close.png'))

    @cached_property
    def explorerIcon(self):
        return QtGui.QIcon(self.get_resource('icons/ic_explorer.png'))

context = AppContext()
