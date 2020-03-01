'''
Functions for dealing with files and folders.
'''

import os
import sys
from PySide2 import QtCore, QtGui

def showInFolder(path):
    '''
    Show a file or folder with explorer/finder.
    Source: https://stackoverflow.com/a/46019091/3388962
    '''
    path = os.path.abspath(path)
    dirPath = path if os.path.isdir(path) else os.path.dirname(path)
    if sys.platform == 'win32':
        args = []
        if not os.path.isdir(path):
            args.append('/select,')
        args.append(QtCore.QDir.toNativeSeparators(path))
        if QtCore.QProcess.startDetached('explorer', args):
            return
    elif sys.platform == 'darwin':
        args = []
        args.append('-e')
        args.append('tell application "Finder"')
        args.append('-e')
        args.append('activate')
        args.append('-e')
        args.append(f'select POSIX file "{path}"')
        args.append('-e')
        args.append('end tell')
        args.append('-e')
        args.append('return')
        if not QtCore.QProcess.execute('/usr/bin/osascript', args):
            return
        #if not QtCore.QProcess.execute('/usr/bin/open', [dirPath]):
        #    return
    # Fallback.
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(dirPath))


if __name__ == '__main__':
    # showInFolder('..')
    showInFolder(r'C:\Dev\ImageWAO\environment.yml')