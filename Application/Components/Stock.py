import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5.QtWidgets import *
import re

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
    
class CustomHeader(QHeaderView):
    def __init__(self, header,labels, parent= None):
        super().__init__(QtCore.Qt.Horizontal, parent) 
        self.main_header = header
        self.setModel(CustomHeaderModel(labels))
        self.sectionResized.connect(self.updateSizes)
        self.main_header.sectionResized.connect(self.updateSizes)
        self.setGeometry(0, 0, header.width(), header.height())
        
        # Configure header behavior
        self.setSectionsClickable(True)
        self.setSectionsMovable(True)
        self.setStretchLastSection(True)
        self.setSectionResizeMode(QHeaderView.Interactive)
        

    def updateSizes(self):
        for i in range(self.count()):
            self.resizeSection(i, self.main_header.sectionSize(i))
    
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
            button.palette.setColor(QtGui.QPalette.Background, QtGui.QColor(QtCore.Qt.blue));
            button.palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(QtCore.Qt.blue));

            #button.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(QtGui.QColor(QtCore.Qt.blue)));


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

        def onButtonEdit(self, id):
            query = QSqlQuery()
            query.prepare("""
                SELECT p.id, p.name, p.sku, p.qty, p.sell_price, p.purchase_price, p.category_id, c.name as category_name
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                WHERE p.id=?
            """)
            query.addBindValue(id)
            query.exec_()
            query.first()

            idIndex = query.record().indexOf("id")
            nameIndex = query.record().indexOf("name")
            skuIndex = query.record().indexOf("sku")
            qtyIndex = query.record().indexOf("qty")
            sellIndex = query.record().indexOf("sell_price")
            purchaseIndex = query.record().indexOf("purchase_price")

            self.updateUI = QDialog()
            self.updateUI.setWindowTitle("Update Product")
            self.updateUI.setObjectName("Update Product")
            self.updateUI.resize(250, 230)
            self.updateUI.setWindowFlags(self.updateUI.windowFlags() & QtCore.Qt.CustomizeWindowHint)
            self.updateUI.setWindowFlags(self.updateUI.windowFlags() & ~QtCore.Qt.WindowMinMaxButtonsHint)

            self.labelName = QLabel("Name:", self.updateUI)
            self.labelName.move(20, 20)
            self.inputName = QLineEdit(self.updateUI)
            self.inputreg_ex = QtCore.QRegExp("^[a-zA-Z ]*$")
            self.input_validator = QtGui.QRegExpValidator(self.inputreg_ex, self.inputName)
            self.inputName.setText(str(query.value(nameIndex)))
            self.inputName.move(100, 15)

            self.labelSku = QLabel("Sku:", self.updateUI)
            self.labelSku.move(20, 50)
            self.inputSku = QLineEdit(self.updateUI)
            self.skureg_ex = QtCore.QRegExp("^[0-9]*$")
            self.sku_validator = QtGui.QRegExpValidator(self.skureg_ex, self.inputSku)
            self.inputSku.setValidator(self.sku_validator)
            self.inputSku.setText(str(query.value(skuIndex)))
            self.inputSku.move(100, 45)

            self.labelQty = QLabel("Quantity:", self.updateUI)
            self.labelQty.move(20, 80)
            self.inputQty = QLineEdit(self.updateUI)
            self.qtyreg_ex = QtCore.QRegExp("^[0-9]*$")
            self.qty_validator = QtGui.QRegExpValidator(self.qtyreg_ex, self.inputQty)
            self.inputQty.setValidator(self.qty_validator)
            self.inputQty.setText(str(query.value(qtyIndex)))
            self.inputQty.move(100, 75)

            self.labelSelling = QLabel("Selling(LKR):", self.updateUI)
            self.labelSelling.move(20, 110)
            self.inputSelling = QLineEdit(self.updateUI)
            self.sellingreg_ex = QtCore.QRegExp("^[0-9]*$")
            self.selling_validator = QtGui.QRegExpValidator(self.sellingreg_ex, self.inputSelling)
            self.inputSelling.setValidator(self.selling_validator)
            self.inputSelling.setText(str(query.value(sellIndex)))
            self.inputSelling.move(100, 105)

            self.labelPurchase = QLabel("Purchase(LKR):", self.updateUI)
            self.labelPurchase.move(20, 140)
            self.inputPurchase = QLineEdit(self.updateUI)
            self.purchasereg_ex = QtCore.QRegExp("^[0-9]*$")
            self.purchase_validator = QtGui.QRegExpValidator(self.purchasereg_ex, self.inputPurchase)
            self.inputPurchase.setValidator(self.purchase_validator)
            self.inputPurchase.setText(str(query.value(purchaseIndex)))
            self.inputPurchase.move(100, 135)

            self.category = QComboBox(self.updateUI)
            categories = self.parent().load_categories()
            selected_category_id = query.value(6)

            for cat_id, cat_name in categories:
                self.category.addItem(cat_name, cat_id)
                if cat_id == selected_category_id:
                    self.category.setCurrentText(cat_name)
            
            self.labelCategory = QLabel("Category:", self.updateUI)
            self.labelCategory.move(20, 170)
            self.category.move(100, 165)

            self.updateButton = QPushButton("Save",self.updateUI)
            self.updateButton.setObjectName(str(query.value(idIndex)))
            self.updateButton.clicked.connect(self.onButtonUpdate)
            self.updateButton.move(100, 200)
            self.updateUI.show()


        def onButtonUpdate(self):
            self.id  = self.sender().objectName()
            name     = self.inputName.text()
            sku      = self.inputSku.text()
            qty      = self.inputQty.text()
            selling  = self.inputSelling.text()
            purchase = self.inputPurchase.text()
            category_id = self.category.currentData()
            MessageBox = QMessageBox()
            if name == "":
               self.inputName.setStyleSheet("border: 1px solid red") 
            elif  sku == "":
               self.inputSku.setStyleSheet("border: 1px solid red")  
            elif  qty == "":
               self.inputQty.setStyleSheet("border: 1px solid red")  
            elif  selling == "":
               self.inputSelling.setStyleSheet("border: 1px solid red") 
            elif  purchase == "":
               self.inputPurchase.setStyleSheet("border: 1px solid red") 
            else:
                try:
                    query = QSqlQuery()
                    query.prepare("UPDATE products SET name=:name, sku=:sku, qty=:qty, sell_price=:sell_price, purchase_price=:purchase_price, category_id=:category_id  WHERE id=:id");
                    query.bindValue(":name", name)
                    query.bindValue(":sku", sku)
                    query.bindValue(":qty", qty)
                    query.bindValue(":sell_price", selling)
                    query.bindValue(":purchase_price", purchase)
                    query.bindValue(":category_id", category_id)
                    query.bindValue(":id", self.id)
                    query.exec_()
                    MessageBox.setIcon(QMessageBox.Information)
                    MessageBox.setText("Product has been updated successfully!")
                    MessageBox.setWindowTitle("Success")
                    MessageBox.setStandardButtons(QMessageBox.Ok)
                    MessageBox.exec()
                    self.parent().initializedModel()
                    self.updateUI.close()
                except Exception as e:
                    print("Oops!", e.__class__, "occurred.")
                    MessageBox.setIcon(QMessageBox.Warning)
                    MessageBox.setText("Something went wrong, please try again later")
                    MessageBox.setWindowTitle("Error")
                    MessageBox.setStandardButtons(QMessageBox.Ok)
                    MessageBox.exec()

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
                        self.onButtonEdit(data[index.row()][0])
                        #print(data[index.row()][0])
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
            button.palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(QtCore.Qt.red));

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


        def onButtonDelete(self, id):             
           MessageBox = QMessageBox()
           MessageBox.setIcon(QMessageBox.Information)
           MessageBox.setText("Are you sure you want to delete?")
           MessageBox.setWindowTitle("Warning")
           MessageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
           returnValue = MessageBox.exec()
           if returnValue == QMessageBox.Yes:
                try:
                    query = QSqlQuery()
                    query.prepare("DELETE FROM products WHERE id=:id");
                    query.bindValue(":id", id)
                    query.exec_()
                    MessageBox.setIcon(QMessageBox.Information)
                    MessageBox.setText("Product has been deleted successfully!")
                    MessageBox.setWindowTitle("Success")
                    MessageBox.setStandardButtons(QMessageBox.Ok)
                    MessageBox.exec()
                    self.parent().initializedModel()
                except Exception as e:
                    MessageBox.setIcon(QMessageBox.Warning)
                    MessageBox.setText("Something went wrong, please try again later")
                    MessageBox.setWindowTitle("Error")
                    MessageBox.setStandardButtons(QMessageBox.Ok)
                    MessageBox.exec()


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
                        self.onButtonDelete(data[index.row()][0])
            return True

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

class StockView(QWidget):
    def __init__(self, parent=None):
        super(StockView, self).__init__(parent)
        self.db = self.initialize_database()
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
        self.tableView = QTableView()
        self.tableView.setModel(self.queryModel)
        self.tableView.setSortingEnabled(True)
        self.add_filter_functionality()
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
        self.tableView.resizeColumnsToContents();
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
        self.resize(600, 300)

    def setUpConnect(self):
        self.prevButton.clicked.connect(self.onPrevPage)
        self.nextButton.clicked.connect(self.onNextPage)
        self.switchPageButton.clicked.connect(self.onSwitchPage)

    def initialize_database(self):
            db_name = "qt_sql_default_connection"
            if QSqlDatabase.contains(db_name):
                db = QSqlDatabase.database(db_name)
                db.close()
                QSqlDatabase.removeDatabase(db_name)
            
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName("Data/database.db")
            if not db.open():
                print("Failed to open database")
                return None
            return db

    def initializedModel(self):
        if not self.db or not self.db.isOpen():
            self.db = self.initialize_database()
            
        sql = "SELECT id as 'ID', name as 'Product Name', sku as 'SKU', qty as 'Quantity', " \
            "sell_price as 'Selling Price', purchase_price as 'Purchase Price' FROM products"
        self.queryModel.setQuery(sql, self.db)
        
        self.proxy = QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.queryModel)
        self.proxy.setFilterKeyColumn(2)  # Set filter to SKU column
        self.totalRecordCount = self.queryModel.rowCount()
        
        if self.totalRecordCount % self.pageRecordCount == 0:
            self.totalPage = self.totalRecordCount / self.pageRecordCount
        else:
            self.totalPage = int(self.totalRecordCount / self.pageRecordCount) + 1
        
        sql = "SELECT id as 'ID', name as 'Product Name', sku as 'SKU', qty as 'Quantity', " \
            "sell_price as 'Selling Price', purchase_price as 'Purchase Price' " \
            "FROM products limit %d,%d" % (0, self.pageRecordCount)
        self.queryModel.setQuery(sql, self.db)
        
        self.tableView.setModel(self.proxy)
        data_labels = ["ID", "Product Name", "SKU", "Quantity", "Selling Price", "Purchase Price", "Edit", "Delete"]
        CustomHeader(self.tableView.horizontalHeader(), data_labels)
        
        self.tableView.model().layoutChanged.emit()
        self.tableView.model().insertColumn(6, QtCore.QModelIndex())
        self.tableView.model().insertColumn(7, QtCore.QModelIndex())
        self.tableView.setItemDelegateForColumn(6, DelegateEdit(self))
        self.tableView.setItemDelegateForColumn(7, DelegateDelete(self))

    def load_categories(self):
            query = QSqlQuery()
            query.exec_("SELECT id, name FROM categories ORDER BY name")
            categories = []
            while query.next():
                categories.append((query.value(0), query.value(1)))
            return categories

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

    def queryRecord(self, limitIndex):
        sql = "SELECT id as 'ID', name as 'Product Name', sku as 'SKU', qty as 'Quantity', " \
                "sell_price as 'Selling Price', purchase_price as 'Purchase Price' " \
                "FROM products limit %d,%d" % (limitIndex, self.pageRecordCount)
        self.queryModel.setQuery(sql)
        
        self.tableView.model().layoutChanged.emit()
        self.tableView.model().insertColumn(6, QtCore.QModelIndex())
        self.tableView.model().insertColumn(7, QtCore.QModelIndex())
        self.tableView.setItemDelegateForColumn(6, DelegateEdit(self))
        self.tableView.setItemDelegateForColumn(7, DelegateDelete(self))

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

    def closeEvent(self):
        if self.db:
            self.db.close()
            QSqlDatabase.removeDatabase(self.db.connectionName())
        super().closeEvent(event)

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
        self.proxy.setFilterFixedString(text)

    def onAddDialog(self):
        self.dialog = QDialog(self)
        self.dialog.setWindowTitle("Add Product")
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
        self.category = QComboBox()
        categories = self.load_categories()
        for cat_id, cat_name in categories:
            self.category.addItem(cat_name, cat_id)
        self.formlayout = QFormLayout() 
        self.formlayout.addRow(QLabel("Name"), self.name) 
        self.formlayout.addRow(QLabel("Sku"), self.sku) 
        self.formlayout.addRow(QLabel("Quantity"), self.qty) 
        self.formlayout.addRow(QLabel("Selling(LKR)"), self.sell) 
        self.formlayout.addRow(QLabel("Purchase(LKR)"), self.purchase) 
        self.formlayout.addRow(QLabel("Category"), self.category)
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
        category_id = self.category.currentData()
        print(category_id)
        if name == "":
           self.name.setStyleSheet("border: 1px solid red") 
        elif  sku == "":
           self.sku.setStyleSheet("border: 1px solid red")  
        elif  qty == "":
           self.qty.setStyleSheet("border: 1px solid red")  
        elif  sell == "":
           self.sell.setStyleSheet("border: 1px solid red") 
        elif  purchase == "":
           self.purchase.setStyleSheet("border: 1px solid red") 
        else:
            try:
                query = QSqlQuery()
                query.prepare("INSERT INTO products (id,name,sku,qty,sell_price,purchase_price, category_id) "
                              "VALUES (NULL, :name, :sku, :qty, :sell_price, :purchase_price, :category_id)")
                query.bindValue(":name", name)
                query.bindValue(":sku", sku)
                query.bindValue(":qty", qty)
                query.bindValue(":sell_price", sell)
                query.bindValue(":purchase_price", purchase)
                query.bindValue(":category_id", category_id)
                query.exec_()
                self.name.clear()
                self.sku.clear()
                self.qty.clear()
                self.sell.clear()
                self.purchase.clear()
                QMessageBox.question(self, "Success","Product has been added successfully!",QMessageBox.Ok)
                self.initializedModel()
                self.dialog.close()
            except Exception as e:
                print("Oops!", e.__class__, "occurred.")
                QMessageBox.information(self, "Error", "Something went wrong, please try again later")

    def onRightClick(self, pos=None):
            index = self.tableView.indexAt(pos)
            if not index.isValid():
                return
                
            data = []
            model = self.tableView.model()
            for column in range(model.columnCount()):
                index_ = model.index(index.row(), column)
                data.append(str(model.data(index_)))
            
            parent = self.sender()
            globalPos = parent.mapToGlobal(pos)
            menu = QMenu()
            editAction = menu.addAction("Edit")
            deleteAction = menu.addAction("Delete")
            
            action = menu.exec_(globalPos)
            if action == editAction:
                delegate = self.tableView.itemDelegateForColumn(6)
                if isinstance(delegate, DelegateEdit):
                    delegate.onButtonEdit(data[0])
            elif action == deleteAction:
                delegate = self.tableView.itemDelegateForColumn(7)
                if isinstance(delegate, DelegateDelete):
                    delegate.onButtonDelete(data[0])

