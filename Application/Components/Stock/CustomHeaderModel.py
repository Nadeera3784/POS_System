import PyQt5.QtCore as QtCore

class CustomHeaderModel(QtCore.QAbstractItemModel):
    def __init__(self, labels, parent=None):
        super(CustomHeaderModel, self).__init__(parent)
        self.labels = labels

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and section < len(self.labels):
            return self.labels[section]
        return None

    def columnCount(self, parent):
        return len(self.labels)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return None
        if index.column() < len(self.labels):
            return self.labels[index.column()]
        return None

    def index(self, row, column, parent=QtCore.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return 0 if parent.isValid() else 1
    