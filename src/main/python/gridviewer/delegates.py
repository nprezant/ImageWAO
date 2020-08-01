from PySide2 import QtCore, QtGui, QtWidgets


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex,
    ):
        super().paint(painter, option, index)
