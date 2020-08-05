from PySide2 import QtCore


class UserRoles:
    FullResImage = QtCore.Qt.UserRole  # No scaling involved
    EntireImage = QtCore.Qt.UserRole + 1  # Entire image (not cropped into sections)
    ImagePath = QtCore.Qt.UserRole + 2  # Path to the original image
    DrawnItems = QtCore.Qt.UserRole + 3  # Items drawn on this image
