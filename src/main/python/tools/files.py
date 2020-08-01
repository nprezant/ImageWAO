"""
Functions for dealing with files and folders.
"""

import os
import sys
from pathlib import Path

from PySide2 import QtCore, QtGui

from base import config


def showInFolder(path, select=True):
    """
    Show a file or folder with explorer/finder.
    Source: https://stackoverflow.com/a/46019091/3388962

    If `select` is `True`, the file or folder will be selected.
    If `select` is `False`, 
    """
    path = os.path.abspath(path)
    dirPath = path if os.path.isdir(path) else os.path.dirname(path)
    if sys.platform == "win32":
        args = []
        if select:
            args.append("/select,")
        args.append(QtCore.QDir.toNativeSeparators(path))
        if QtCore.QProcess.startDetached("explorer", args):
            return
    elif sys.platform == "darwin":
        args = []
        args.append("-e")
        args.append('tell application "Finder"')
        args.append("-e")
        args.append("activate")
        args.append("-e")
        args.append(f'select POSIX file "{path}"')
        args.append("-e")
        args.append("end tell")
        args.append("-e")
        args.append("return")
        if not QtCore.QProcess.execute("/usr/bin/osascript", args):
            return
        # if not QtCore.QProcess.execute('/usr/bin/open', [dirPath]):
        #    return
    # Fallback.
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(dirPath))


class DirectoryValidator(QtGui.QValidator):
    def validate(self, userInput: str, pos: int):

        # Invalid volume names will cause this to fail.
        # Intermediate allows user to try it and keep typing
        try:
            isDir = Path(userInput).is_dir()
        except OSError:
            return QtGui.QValidator.Intermediate

        # Acceptable if path is a directory, otherwise we might get there
        if isDir:
            return QtGui.QValidator.Acceptable
        else:
            return QtGui.QValidator.Intermediate


class FileNameValidator(QtGui.QValidator):
    """
    Ensures that the file or folder name does not have any
    illegal characters in it.
    """

    def validate(self, userInput: str, pos: int):

        # Indices of invalid characters
        invalids = [1 if s in config.invalidPathCharacters else 0 for s in userInput]

        # Valid if there are no invalid characters
        if sum(invalids) == 0:
            return QtGui.QValidator.Acceptable
        else:
            return QtGui.QValidator.Invalid


if __name__ == "__main__":
    # showInFolder('..')
    showInFolder(r"C:\Dev\ImageWAO\environment.yml")
