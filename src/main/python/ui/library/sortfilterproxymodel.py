from PySide6 import QtCore


class SortFilterProxyModel(QtCore.QSortFilterProxyModel):

    filterOut = []

    def filterAcceptsRow(self, sourceRow, sourceParent):
        # Fetch datetime value.
        index = self.sourceModel().index(sourceRow, 0, sourceParent)
        data = self.sourceModel().data(index)

        # Filter OUT matching files
        if self.filterOut is None:
            return super().filterAcceptsRow(sourceRow, sourceParent)
        elif data.lower() in self.filterOut:
            return False
        else:
            return True
