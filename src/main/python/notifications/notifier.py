
from enum import Enum

from PySide2 import QtCore, QtGui, QtWidgets

from .toaster import QToaster

class ToastOption(Enum):
    Add = 1
    Remove = 2

class Notifier:

    # constant margins
    SIDE_MARGIN = 10
    BOTTOM_MARGIN = 10
    BOTTOM_SCREEN_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__()

        # Parent widget will be used to determine notification
        # geometry location.
        self.parent = parent
        
        self._animating = False
        self._notifications = []
        self._queuedNotifications = []
        self.count = 0

    def notify(self, message):
        toast = QToaster(self.parent)
        toast.closed.connect(lambda: self._removeToast(toast))
        if message != '':
            icon = icon = toast.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
            size = toast.style().pixelMetric(QtWidgets.QStyle.PM_SmallIconSize)
            pix = icon.pixmap(size)
            toast.generate(message, icon=pix, iconAlignment=QtCore.Qt.AlignVCenter)
        elif self.count % 2 == 0:
            icon = toast.style().standardIcon(QtWidgets.QStyle.SP_MessageBoxInformation)
            size = toast.style().pixelMetric(QtWidgets.QStyle.PM_SmallIconSize)
            pix = icon.pixmap(size)
            toast.generate('You rock!', icon=pix, iconAlignment=QtCore.Qt.AlignVCenter)
        elif self.count % 3 == 0:
            icon = toast.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon)
            size = toast.style().pixelMetric(QtWidgets.QStyle.PM_LargeIconSize)
            pix = icon.pixmap(size)
            toast.generate('Nice!\nYou\'ve completed 50 images today!\nReally taking out the trash...\nThis is another line\nAnd yet another\nand another\nboom\nroasted.', icon=pix)
        else:
            icon = toast.style().standardIcon(QtWidgets.QStyle.SP_TrashIcon)
            size = toast.style().pixelMetric(QtWidgets.QStyle.PM_LargeIconSize)
            pix = icon.pixmap(size)
            toast.generate('Nice!\nYou\'ve completed 50 images today!\nReally taking out the trash...', icon=pix)
        self.count += 1
        self._addToast(toast)

    def _addToast(self, toast):
        self._queuedNotifications.append((toast, ToastOption.Add))
        if not self._animating:
            self._readNextToast()

    def _removeToast(self, toast):
        self._queuedNotifications.append((toast, ToastOption.Remove))
        if not self._animating:
            self._readNextToast()

    def _readNextToast(self):
        if len(self._queuedNotifications) == 0:
            print('No toast left!')
            return
        
        if self._animating:
            print('Cannot read toast, currently animating!')
            return

        params = self._queuedNotifications.pop(0)
        self._drawToast(*params)

    def _drawToast(self, toastInQuestion, option):

        self._animating = True
        parentRect = self.parent.rect()

        if option == ToastOption.Add:
            self._notifications.append(toastInQuestion)
        elif option == ToastOption.Remove:
            self._notifications.remove(toastInQuestion)
        else:
            raise ValueError(f'Toast option invalid: {option}')

        basePoint = parentRect.bottomRight() + QtCore.QPoint(-self.BOTTOM_SCREEN_MARGIN, -self.SIDE_MARGIN)

        for toast in reversed(self._notifications):

            # Determine and set position of this toast
            geo = toast.geometry()
            geo.moveBottomRight(
                basePoint + QtCore.QPoint(0, -self.BOTTOM_MARGIN))

            toast.setGeometry(geo)

            # If this is the relevant toast, determine where it
            # should be coming from or going
            otherGeo = toast.geometry()
            if toast is toastInQuestion:
                if option == ToastOption.Add:
                    otherGeo.moveBottomRight(
                        otherGeo.bottomRight() + QtCore.QPoint(0, 10)
                    )
                elif option == ToastOption.Remove:
                    otherGeo.moveBottomRight(
                        otherGeo.bottomRight() + QtCore.QPoint(0, 10)
                    )
            
            # toast.animateIn(geo.move)
            toast.show_()
            basePoint = geo.topRight()

        self._animating = False

    def printToast(self):
        print(f'{len(self._notifications)} notifications')


