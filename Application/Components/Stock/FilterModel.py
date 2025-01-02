import PyQt5.QtCore as QtCore

class FilterModel(QtCore.QSortFilterProxyModel):
    def __init__(self, filters):
        super().__init__()
        self.filters = filters

    def filterAcceptsRow(self, row, modelindex):
        for i, filter in enumerate(self.filters):
            if filter not in str(self.sourceModel().index(row, i).data()):
                return False
        return True
