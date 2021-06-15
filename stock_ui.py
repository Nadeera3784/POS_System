import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5.QtWidgets import *
import re

# class ButtonDelegate(QItemDelegate):

#     def __init__(self, parent):
#        QItemDelegate.__init__(self, parent)

#     def createEditor(self, parent, option, index):
#         combo = QPushButton(str(index.data()), parent)

#         #self.connect(combo, QtCore.SIGNAL("currentIndexChanged(int)"), self, QtCore.SLOT("currentIndexChanged()"))
#         combo.clicked.connect(self.currentIndexChanged)
#         return combo
        
#     def setEditorData(self, editor, index):
#         editor.blockSignals(True)
#         #editor.setCurrentIndex(int(index.model().data(index)))
#         editor.blockSignals(False)
        
#     def setModelData(self, editor, model, index):
#         model.setData(index, editor.text())
        
#     @QtCore.pyqtSlot()
#     def currentIndexChanged(self):
#         print('clicked')
#         self.commitData.emit(self.sender())

class FilterModel(QtCore.QSortFilterProxyModel):
    def __init__(self, filters):
        super().__init__()
        self.filters = filters

    def filterAcceptsRow(self, row, modelindex):
        for i, filter in enumerate(self.filters):
            if filter not in str(self.sourceModel().index(row, i).data()):
                return False
        return True

class FilterDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_elements()

    def init_elements(self):
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)

        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self.accept)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(cancelButton)
        hbox.addWidget(okButton)

        self.regex = QLineEdit()

        vbox = QVBoxLayout()
        vbox.addWidget(self.regex)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setWindowTitle('Filter Column')

#model for the headerview defined below
class MyHeaderModel(QtCore.QAbstractItemModel):
    def __init__(self, labels, parent = None):
        super(MyHeaderModel, self).__init__(parent)
        self.headerDataChanged.connect(lambda: ...)
        self.data_ = self.fill_labels_spacing(labels, parent)
        
    def headerData(self, section, orientation, role):
        return QtCore.QVariant(self.data_[section])

    def columnCount(self,parent):
        return 7#----------
    def data(self, index, role = QtCore.Qt.DisplayRole):
        return index.internalPointer().data(index.column())
    def index(self, row, column, parent = QtCore.QModelIndex()):
        return QtCore.QModelIndex()
    def parent(self, index):
        return QtCore.QModelIndex()

    def rowCount(self, parent = QtCore.QModelIndex()):
        return 0

    def fill_labels_spacing(self, labels, parent):
        cell_width = 800 // self.columnCount(self) + 1 #616 width is the updated table width after headerview has been spawned
        
        normal_cell_width = parent.geometry().width() // self.columnCount(self) + 1

        new_label_list = []
        for i, label in enumerate(labels):
            if i == len(labels) - 1:
                for i in range(round(0.33 * cell_width)):# use 1/3 to get one third of the 
                    label = " "+label
                new_label_list.append(label)
            else:
                for i in range(round(0.5 * normal_cell_width) ):
                    label = " "+label
                new_label_list.append(label)
        return new_label_list
    
#the header is responsible for merging the  column , in this case, last 2 columns
#it uses the custom header data model which was implemented above
class MyHeader(QHeaderView):
    def __init__(self, header,labels, parent= None):
        super().__init__(QtCore.Qt.Horizontal, header)
        self.main_header = header
        self.setModel(MyHeaderModel( labels, self))
        self.resizeSection(6, self.getSectionSizes(6,7))
        self.sectionResized.connect(self.updateSizes)
        self.horizontalScrollBar().valueChanged.connect(self.updateOffset)
        self.setGeometry(0, 0, header.width(), header.height())
        self.updateOffset()
        self.main_header.installEventFilter(self)
        self.main_header.setCascadingSectionResizes(False)
        self.main_header.setSortIndicatorShown(False)
        self.main_header.setStretchLastSection(True)
        

    def updateSizes(self):
        self.setOffset(self.main_header.offset())
        self.main_header.resizeSection(7, self.main_header.sectionSize(7) + (self.sectionSize(6) - self.getSectionSizes(6, 7)))
    
    def updateOffset(self):
        self.setOffset(self.main_header.offset())
        
    
    def eventFilter(self, object, event):
        if object == self.main_header:
            if event.type() == QtCore.QEvent.Resize:
                self.setOffset(self.main_header.offset())
                self.setGeometry(0, 0, self.main_header.width(), self.main_header.height())
            return False
        return super().eventFilter(object, event)

    def getSectionSizes(self, first,  second):
        size = 0
        for a in range(first, second + 1):
            size += self.main_header.sectionSize(a)
        return size


class DelegateEdit(QItemDelegate):
        def __init__(self, owner):
            super().__init__(owner)
            self.owner = owner
        #def createEditor(self, parent, option, index):
        #    return DelegateEdit(parent)    
        def createEditor(self, parent, option, index):
            self.lineEdit = QLineEdit(parent)
            self.lineEdit.textChanged.connect(self.emitCommitData) 
            self.lineEdit.setText(self.getValue().toString())
            self.lineEdit.setAlignment(Qt.AlignVCenter|Qt.AlignRight)
            self.lineEdit.deselect()
            return self.lineEdit
        def setEditorData(self, editor, index):
            editor.blockSignals(True)
            editor.setCurrentIndex(int(index.model().data(index)))
            editor.blockSignals(False)
        def paint(self, painter, option, index):
            value = index.data(QtCore.Qt.DisplayRole)
            style = QApplication.style()
            button = QStyleOptionButton()
            button.text = "Edit"

            x = option.rect.left() + 10
            y = option.rect.top() + 5
            w = option.rect.width() - 20
            h = option.rect.height() - 10
            button.rect = QtCore.QRect(x,y, w, h)

            button.state = QStyle.State_Enabled

            style.drawControl(QStyle.CE_PushButton, button, painter)
            QItemDelegate.paint(self, painter, option, index)

        def setModelData(self, editor, model, index):
            value = editor.currentText()
            model.setData(index, QtCore.Qt.DisplayRole, QtCore.QVariant(value))

        def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)

        def editorEvent(self, event, model, option, index):
            x = option.rect.left() + 10
            y = option.rect.top() + 5
            w = option.rect.width() - 20
            h = option.rect.height() - 10
            data = []
            for row in range(model.rowCount()):
                data.append([])
                for column in range(model.columnCount()):
                    index_ = model.index(row, column)
                    data[row].append(str(model.data(index_)))

            if event.type() == QtCore.QEvent.MouseButtonRelease:
                click_x = event.x()
                click_y = event.y()
                if(click_x > x and click_x < (x + w)):
                    if(click_y > y and click_y < (y + h)):
                        print(data[index.row()][0])
            return True

class DelegateDelete(QItemDelegate):
        def __init__(self, owner):
            super().__init__(owner)
            self.owner = owner
        def createEditor(self, parent, option, index):
            self.editor = QPushButton("Hello",parent)
            return self.editor
        def paint(self, painter, option, index):
            value = index.data(QtCore.Qt.DisplayRole)
            style = QApplication.style()
            button = QStyleOptionButton()
            button.text = "Delete"

            x = option.rect.left() + 10
            y = option.rect.top() + 5
            w = option.rect.width() - 20
            h = option.rect.height() - 10
            button.rect = QtCore.QRect(x,y, w, h)

            button.state = QStyle.State_Enabled

            style.drawControl(QStyle.CE_PushButton, button, painter)
            QItemDelegate.paint(self, painter, option, index)

        def setModelData(self, editor, model, index):
            value = editor.currentText()
            model.setData(index, QtCore.Qt.DisplayRole, QtCore.QVariant(value))
        def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)

        def editorEvent(self, event, model, option, index):
            x = option.rect.left() + 10
            y = option.rect.top() + 5
            w = option.rect.width() - 20
            h = option.rect.height() - 10

            ##model_ = self.owner.model
            data = []
            for row in range(model.rowCount()):
                data.append([])
                for column in range(model.columnCount()):
                    index_ = model.index(row, column)
                    data[row].append(str(model.data(index_)))

            if event.type() == QtCore.QEvent.MouseButtonRelease:
                click_x = event.x()
                click_y = event.y()
                if(click_x > x and click_x < (x + w)):
                    if(click_y > y and click_y < (y + h)):
                       print(data[index.row()][0])
            return True

# HaveChildrenRole = QtCore.Qt.UserRole

# class CustomSqlModel(QSqlQueryModel):
#     def data(self, index, role):
#         value = super(CustomSqlModel, self).data(index, role)
#         #if value is not None and role == QtCore.Qt.DisplayRole:
#             #if index.column() == 3:
#             #    return value.upper()
#         if role == QtCore.Qt.TextColorRole and index.column() == 1:
#             return QtGui.QColor(QtCore.Qt.blue)
#         return value


class CheckboxSqlModel(QSqlQueryModel):
    def __init__(self, column):
        super(CheckboxSqlModel, self).__init__()
        self.column = column
        self.checkboxes = list() #List of checkbox states
        self.first = list() #Used to initialize checkboxes

    def flags(self, index):
        flags = QSqlQueryModel.flags(self, index)
        if index.column() == self.column:
            flags |= QtCore.Qt.ItemIsUserCheckable
        return flags

    def data(self, index, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if index.column() == self.column and role == QtCore.Qt.CheckStateRole:
            #Used to initialize
            if row not in self.first :
                index = self.createIndex(row, self.column)
                self.first.append(row)
                self.checkboxes.append(False)
                return QtCore.Qt.Unchecked
            #if checked
            elif self.checkboxes[row]:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked
        else:
            return QSqlQueryModel.data(self, index, role)

    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        row = index.row()
        if index.column() == self.column and role == QtCore.Qt.CheckStateRole:
            if value:
                print(value);
                self.checkboxes[row] = True
            else:
                self.checkboxes[row] = False
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

class StockUI(QWidget):
    def __init__(self, parent=None):
        super(StockUI, self).__init__(parent)
        self.db = None
        self.layout = QVBoxLayout()

        self.top_box_layout = QHBoxLayout()

        self.add_button = QPushButton("Add +")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("SKU");
        self.search_button = QPushButton("Search")
        self.search_box.textChanged.connect(self.onSearchChanged)
        self.add_button.clicked.connect(self.onAddDialog)
        #self.hbox.addStretch()
        self.top_box_layout.addWidget(self.add_button)
        self.top_box_layout.addWidget(self.search_box)
        self.top_box_layout.addWidget(self.search_button)
        self.layout.addLayout(self.top_box_layout)

        self.queryModel = QSqlQueryModel()
        #self.queryModel = CustomSqlModel()
        #self.queryModel = QtGui.QStandardItemModel()
        #self.queryModel.setHorizontalHeaderLabels(['ID', 'Name', 'SKU', 'QTY', 'SELL', 'PURCHASE'])
        # exper
        #self.queryModel = QSqlTableModel(self.db)
        #epri
        # Table View
        self.tableView = QTableView()
        self.tableView.setModel(self.queryModel)
        #self.tableView.setSortingEnabled(True)
        self.add_filter_functionality()
        #delegate_0 = Column0Delegate()
        #self.tableView.setItemDelegateForColumn(4, delegate_0)
        #self.tableView.setItemDelegateForColumn(6, ButtonDelegate(self))

        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.onRightClick)

        self.totalPageLabel = QLabel()
        self.currentPageLabel = QLabel()
        self.switchPageLineEdit = QLineEdit()
        self.prevButton = QPushButton("Prev")
        self.nextButton = QPushButton("Next")
        self.switchPageButton = QPushButton("Switch")
        # Current Page
        self.currentPage = 1
        # PageCount
        self.totalPage = None
        # Total Records
        self.totalRecordCount = None
        # Number of records per page
        self.pageRecordCount = 20

        self.initUI()
        self.initializedModel()
        self.setUpConnect()
        self.updateStatus()

    def initUI(self):
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tableView)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.prevButton)
        hLayout.addWidget(self.nextButton)
        hLayout.addWidget(QLabel("Jump To"))
        self.switchPageLineEdit.setFixedWidth(40)
        hLayout.addWidget(self.switchPageLineEdit)
        hLayout.addWidget(QLabel("page"))
        hLayout.addWidget(self.switchPageButton)
        hLayout.addWidget(QLabel("Current page:"))
        hLayout.addWidget(self.currentPageLabel)
        hLayout.addWidget(QLabel("Total pages:"))
        hLayout.addWidget(self.totalPageLabel)
        hLayout.addStretch(1)

        self.layout.addLayout(hLayout)
        self.setLayout(self.layout)

        self.setWindowTitle("DataGrid")
        self.resize(600, 300)

    def setUpConnect(self):
        self.prevButton.clicked.connect(self.onPrevPage)
        self.nextButton.clicked.connect(self.onNextPage)
        self.switchPageButton.clicked.connect(self.onSwitchPage)

    def initializedModel(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("database/database.db")
        if not self.db.open():
            return False
        sql = "SELECT * FROM products"
        self.queryModel.setQuery(sql, self.db)
        self.queryModel.setHeaderData(0, QtCore.Qt.Horizontal, "ID")
        self.queryModel.setHeaderData(1, QtCore.Qt.Horizontal, "Name")
        self.queryModel.setHeaderData(2, QtCore.Qt.Horizontal, "SKU")
        self.queryModel.setHeaderData(3, QtCore.Qt.Horizontal, "QTY")
        self.queryModel.setHeaderData(4, QtCore.Qt.Horizontal, "SELL")
        self.queryModel.setHeaderData(5, QtCore.Qt.Horizontal, "PURCHASE")
        #self.queryModel.setHeaderData(6, QtCore.Qt.Horizontal, "Edit")
        #self.queryModel.setHeaderData(7, QtCore.Qt.Horizontal, "Edit2")

        self.queryModel.setHeaderData(6, QtCore.Qt.Horizontal,  "Edit");

        self.proxy = QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.queryModel)
        self.proxy.setFilterKeyColumn(1)
        self.totalRecordCount = self.queryModel.rowCount()
        if self.totalRecordCount % self.pageRecordCount == 0:
            self.totalPage = self.totalRecordCount / self.pageRecordCount
        else:
            self.totalPage = int(self.totalRecordCount / self.pageRecordCount) + 1
        # Show Page 1
        sql = "SELECT * FROM products limit %d,%d" % (0, self.pageRecordCount)
        self.queryModel.setQuery(sql, self.db)
        self.tableView.setModel(self.proxy)

        # self.btnEdit = QPushButton('Edit')
        # self.button_layout = QHBoxLayout() 
        # self.button_layout.addWidget(self.btnEdit)
        # self.buttons_widget = QWidget()
        # self.buttons_widget.setLayout(self.button_layout)

        # self.queryModel.setData(self.queryModel.index(1, 6), self.buttons_widget)
        # self.tableView.setIndexWidget(self.queryModel.index(1, 7, QtCore.QModelIndex()), QPushButton("button"))
        #self.queryModel.insertRow(self.queryModel.rowCount(QtCore.QModelIndex()));
        #self.tableView.setItemDelegateForColumn(6, DelegateEdit(self))
        #self.tableView.setItemDelegateForColumn(7, DelegateDelete(self))
        data_labels = ["ID", "Name", "SKU", "QTY", "SELL", "PURCHASE", "ACTION", "ACTION2"]
        #MyHeader(self.tableView.horizontalHeader(), data_labels)
        #self.tableView.setItemDelegateForColumn(6, self.buttons_widget)
        #self.tableView.model().layoutChanged.emit()
        self.tableView.model().insertColumn(6, QtCore.QModelIndex())
        self.tableView.model().insertColumn(7, QtCore.QModelIndex())
        #self.tableView.setIndexWidget(self.tableView.model().index(1, 6), QPushButton("Delete"))
        self.tableView.setItemDelegateForColumn(6, DelegateEdit(self))
        self.tableView.setItemDelegateForColumn(7, DelegateDelete(self))
        MyHeader(self.tableView.horizontalHeader(), data_labels)

    def onPrevPage(self):
        self.currentPage -= 1
        limitIndex = (self.currentPage - 1) * self.pageRecordCount
        self.queryRecord(limitIndex)
        self.updateStatus()

    def onNextPage(self):
        self.currentPage += 1
        limitIndex = (self.currentPage - 1) * self.pageRecordCount
        self.queryRecord(limitIndex)
        self.updateStatus()

    def onSwitchPage(self):
        szText = self.switchPageLineEdit.text()
        pattern = re.compile('^[0-9]+$')
        match = pattern.match(szText)
        if not match:
            QMessageBox.information(self, "Tips", "please enter a number.")
            return
        if szText == "":
            QMessageBox.information(self, "Tips", "Please enter a jump page.")
            return
        pageIndex = int(szText)
        if pageIndex > self.totalPage or pageIndex < 1:
            QMessageBox.information(self, "Tips", "No page specified, re-enter.")
            return

        limitIndex = (pageIndex - 1) * self.pageRecordCount
        self.queryRecord(limitIndex)
        self.currentPage = pageIndex
        self.updateStatus()

    # Query records based on paging
    def queryRecord(self, limitIndex):
        sql = "SELECT * FROM products limit %d,%d" % (limitIndex, self.pageRecordCount)
        self.queryModel.setQuery(sql)

    # Update Spatial Status
    def updateStatus(self):
        self.currentPageLabel.setText(str(self.currentPage))
        self.totalPageLabel.setText(str(self.totalPage))
        if self.currentPage <= 1:
            self.prevButton.setEnabled(False)
        else:
            self.prevButton.setEnabled(True)

        if self.currentPage >= self.totalPage:
            self.nextButton.setEnabled(False)
        else:
            self.nextButton.setEnabled(True)

    def closeEvent(self, event):
        self.db.close()

    def add_filter_functionality(self):
        def show_filter(logical_index):
            dialog = FilterDialog(self)
            if not dialog.exec_():
                return
            filtertext = dialog.regex.text()
            self.filters.filters[logical_index] = filtertext
            self.filters.modelReset.emit()
        columncount = int(self.tableView.horizontalHeader().count())
        self.filters = FilterModel([""] * 6)
        self.filters.setSourceModel(self.queryModel)
        self.tableView.setModel(self.filters)
        self.filters.modelReset.emit()
        header = self.tableView.horizontalHeader()
        header.sectionDoubleClicked.connect(show_filter)

    def onSearchChanged(self, text):
        regex = "^{}".format(text)
        self.proxy.setFilterRegExp(QtCore.QRegExp(regex, QtCore.Qt.CaseInsensitive))

    def onAddDialog(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Add Stock")
        self.formGroupBox = QGroupBox("New Product") 
        self.onlyInt = QtGui.QIntValidator()
        self.sku = QLineEdit() 
        self.sku.setValidator(self.onlyInt)
        self.qty = QLineEdit() 
        self.qty.setValidator(self.onlyInt)
        self.sell = QLineEdit() 
        self.sell.setValidator(self.onlyInt)
        self.purchase = QLineEdit() 
        self.purchase.setValidator(self.onlyInt)
        self.name = QLineEdit() 
        self.formlayout = QFormLayout() 
        self.formlayout.addRow(QLabel("Name"), self.name) 
        self.formlayout.addRow(QLabel("Sku"), self.sku) 
        self.formlayout.addRow(QLabel("Quantity"), self.qty) 
        self.formlayout.addRow(QLabel("Selling(LKR)"), self.sell) 
        self.formlayout.addRow(QLabel("Purchase(LKR)"), self.purchase) 
        self.formGroupBox.setLayout(self.formlayout) 
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Add", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.buttonBox.rejected.connect(self.dialog.reject)
        self.buttonBox.accepted.connect(self.onAddProductData)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.formGroupBox) 
        self.layout.addWidget(self.buttonBox)
        self.dialog.setLayout(self.layout)
        self.dialog.exec_()

    def onAddProductData(self):
        name      = self.name.text().strip()
        sku       = self.sku.text().strip()
        qty       = self.qty.text().strip()
        sell      = self.sell.text().strip()
        purchase  = self.purchase.text().strip()
        if(name != ""):
            query = QSqlQuery()
            query.prepare("INSERT INTO products (id,name,sku,qty,sell_price,purchase_price) "
                          "VALUES (NULL, :name, :sku, :qty, :sell_price, :purchase_price)")
            query.bindValue(":name", name)
            query.bindValue(":sku", sku)
            query.bindValue(":qty", qty)
            query.bindValue(":sell_price", sell)
            query.bindValue(":purchase_price", purchase)
            query.exec_()
            self.name.clear()
            self.sku.clear()
            self.qty.clear()
            self.sell.clear()
            self.purchase.clear()
            QMessageBox.question(self, "Success","Product has been added successfully!",QMessageBox.Ok)
            self.initializedModel()

    # def onRightClick(self, pos=None):   
    #     if self.tableView.selectionModel().selection().indexes():
    #         for i in self.tableView.selectionModel().selection().indexes():
    #             row, column = i.row(), i.column()

    #         parent = self.sender()
    #         pPos = parent.mapToGlobal(QtCore.QPoint(5, 20))
    #         mPos = pPos+pos
    #         print(parent);
    #         self.rcMenu.move(mPos)
    #         self.rcMenu.show()



    def onRightClick(self, pos=None):
        parent = self.sender()
        globalPos = parent.mapToGlobal(pos)
        globalPos.setX( globalPos.x() + 20)
        globalPos.setY( globalPos.y() + 30)
        mPos = globalPos+pos
        menu = QMenu()
        menu.addAction("Edit")
        menu.addAction("Delete")
        selectedItem = menu.exec_(globalPos)
        if selectedItem:
            if selectedItem.text() == "Edit":
                print ("clicked on Edit")
            #self.DoEdit(widge
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DataGrid()
#     window.show()
#     sys.exit(app.exec_())


