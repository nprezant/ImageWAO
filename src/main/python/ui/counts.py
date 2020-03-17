'''
Form used to add counts of animals.
'''

from PySide2 import QtCore, QtGui, QtWidgets

from tools import distanceToRect

class CountForm(QtWidgets.QFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(100,100)
        self.setStyleSheet('''
            CountForm {
                border: 1px solid black;
                border-radius: 4px; 
                background: red;
            }
        ''')

        # The popup window will hide itself when the mouse moves this distance
        # away from the window
        self._hidePopupDistance = 30

        # Install an eventFilter so that we can track mouse positions
        # and hide the popup when the user doesn't mouse over it.
        # Mouse events exist in the viewport, if the parent has one.
        try:
            filterable = self.parent().viewport()
        except AttributeError:
            filterable = self.parent()
        finally:
            filterable.installEventFilter(self)

        # Don't show on construction.
        # Parent must call "popup" to show
        self.hide()

    def popup(self, pos):
        '''
        Show the Count Form as a popup window.
        Hide form if mouse does not immediately move it.
        '''

        # Show
        self.raise_()
        self.move(pos)
        self.show()

        # Setup mouse tracking. This is required to receive mouse events
        # even when no mouse buttons are pressed.
        self._mouseTrackingState = self.parent().hasMouseTracking()
        self.parent().setMouseTracking(True)

    def hidePopup(self):
        '''
        Hides the popup window.
        '''

        # Clean up parent mouse tracking state
        self.parent().setMouseTracking(self._mouseTrackingState)
        self.hide()

    def eventFilter(self, source:QtCore.QObject, event:QtCore.QEvent):
        '''
        Grabs mouse events from outside the widget
        '''
        if event.type() == QtCore.QEvent.MouseMove:

            # If we are not visible, no need to compute anything
            if self.isVisible() == False:
                pass

            else:
                # Compute distance to mouse cursor.
                d = distanceToRect(event.pos(), self.geometry())
                print(F'Movement on viewport: {d}')

                if d > self._hidePopupDistance:
                    self.hidePopup()

        return super().eventFilter(source, event)

    
