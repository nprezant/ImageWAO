from PySide6 import QtWidgets, QtGui, QtCore

import traceback
from collections import namedtuple
from typing import List


def excepthook(exctype, value, exctb):
    """
    Qt for Python will sometimes drop frames in traceback.
    This should grab those for us.
    https://fman.io/blog/pyqt-excepthook/
    """
    # Enrich traceback with the missing frames from Qt stuff
    enriched_tb = _add_missing_frames(exctb) if exctb else exctb

    # Get traceback as a list of strings.
    # Strings already contain newlines where appropriate
    traceback_text: List[str] = traceback.format_exception(exctype, value, enriched_tb)
    traceback_display = "".join(traceback_text)

    # Display error as a dialog window and attempt to continue
    topLabel = QtWidgets.QLabel()
    topLabel.setText(
        "Error."
    )
    topLabel.setWordWrap(True)

    errorTextEdit = QtWidgets.QTextEdit()
    errorTextEdit.setReadOnly(True)
    errorTextEdit.setWordWrapMode(QtGui.QTextOption.NoWrap)
    errorTextEdit.setText(traceback_display)

    buttonBox = QtWidgets.QDialogButtonBox()
    copyButton = buttonBox.addButton("Copy text", QtWidgets.QDialogButtonBox.ResetRole)
    okayButton = buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(topLabel)
    layout.addWidget(errorTextEdit)
    layout.addWidget(buttonBox)

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Error")
    dialog.setWindowFlags(
        dialog.windowFlags() & (~QtCore.Qt.WindowContextHelpButtonHint)
    )
    dialog.setLayout(layout)

    copyButton.clicked.connect(
        lambda: [errorTextEdit.selectAll(), errorTextEdit.copy()]
    )
    okayButton.clicked.connect(dialog.close)

    dialog.exec()


def _add_missing_frames(tb):
    result = fake_tb(tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
    frame = tb.tb_frame.f_back
    while frame:
        result = fake_tb(frame, frame.f_lasti, frame.f_lineno, result)
        frame = frame.f_back
    return result


fake_tb = namedtuple("fake_tb", ("tb_frame", "tb_lasti", "tb_lineno", "tb_next"))
