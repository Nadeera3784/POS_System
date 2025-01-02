import sys
import re
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIntValidator
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QTableView, QHeaderView, QMenuBar, QGridLayout, QSpinBox, QInputDialog, QMessageBox, QDialog, QTextEdit)
from PyQt5.QtCore import QObject, QDateTime, Qt, QDate
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import json
from Application.Components.Sales.Receipt import ReceiptView

class UIContainer(QObject):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowTitle("POS System v.1.1")
        Form.resize(1800, 900)

        self.categoryLayout = QGridLayout()
        self.categoryButtons = {}
        self.load_categories()

        self.productSection = QVBoxLayout()
        
        # Search Bar
        self.searchBar = QHBoxLayout()
        self.addButton = QPushButton("Add +")
        self.skuSearch = QLineEdit()
        self.skuSearch.setPlaceholderText("SKU")
        self.searchButton = QPushButton("Search")
        for widget in [self.addButton, self.skuSearch, self.searchButton]:
            self.searchBar.addWidget(widget)
        
        # Product Table
        self.productTable = QTableView()
        self.productTable.setMinimumHeight(400)
        self.productTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.productSection.addLayout(self.searchBar)
        self.productSection.addWidget(self.productTable)

        # Cart Section (Right side)
        self.cartSection = QVBoxLayout()
        
        # Cart Header
        self.cartHeader = QHBoxLayout()
        for label in ['Item', 'Qty', 'Price']:
            lbl = QLabel(label)
            lbl.setStyleSheet("font: 75 12pt; color: white;")
            self.cartHeader.addWidget(lbl)

        # Cart Items
        self.cartList = QTableView()
        self.cartList.setMinimumHeight(600)
        
        # Cart Total
        self.totalSection = QVBoxLayout()
        
        # First row
        self.totalRow1 = QHBoxLayout()
        self.subTotalLabel = QLabel("Sub Total : ")
        self.subTotalValue = QLabel("50")
        self.discountLabel = QLabel("Discount : ")
        self.discountValue = QSpinBox()
        self.totalLabel = QLabel("Total Payment : ")
        self.totalValue = QLabel("50")
        
        for widget in [self.subTotalLabel, self.subTotalValue, 
                      self.discountLabel, self.discountValue,
                      self.totalLabel, self.totalValue]:
            self.totalRow1.addWidget(widget)
            
        # Second row
        self.totalRow2 = QHBoxLayout()
        self.paidLabel = QLabel("Paid : ")
        self.paidInput = QLineEdit()
        self.paidInput.textChanged.connect(self.calculate_balance)
        self.balanceLabel = QLabel("Balance : ")
        self.balanceInput = QLineEdit()
        self.balanceInput.setReadOnly(True)
        self.payButton = QPushButton("Pay")
        self.payButton.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        
        for widget in [self.paidLabel, self.paidInput,
                      self.balanceLabel, self.balanceInput,
                      self.payButton]:
            self.totalRow2.addWidget(widget)
            
        self.totalSection.addLayout(self.totalRow1)
        self.totalSection.addLayout(self.totalRow2)

        self.cartSection.addLayout(self.cartHeader)
        self.cartSection.addWidget(self.cartList)
        self.cartSection.addLayout(self.totalSection)

        # Main Layout
        self.mainLayout = QHBoxLayout()
        self.leftSection = QVBoxLayout()
        self.leftSection.addLayout(self.categoryLayout)
        self.leftSection.addLayout(self.productSection)
        
        self.mainLayout.addLayout(self.leftSection, stretch=2)
        self.mainLayout.addLayout(self.cartSection, stretch=1)

        mainWidget = QWidget()
        mainWidget.setLayout(self.mainLayout)
        Form.setCentralWidget(mainWidget)

    def calculate_balance(self):
        try:
            total = float(self.totalValue.text())
            paid = float(self.paidInput.text() or 0)
            balance = paid - total
            self.balanceInput.setText(f"{balance:.2f}")
        except ValueError:
            self.balanceInput.setText("Invalid input")

    def load_categories(self):
        # First clear any existing buttons in the layout and dictionary
        while self.categoryLayout.count():
            item = self.categoryLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.categoryButtons.clear()

        # Load categories from database
        query = QSqlQuery()
        query.exec_("SELECT id, name FROM categories ORDER BY name")
        
        row = 0
        col = 0
        while query.next():
            category_id = query.value(0)
            category_name = query.value(1)
            
            btn = QPushButton(category_name.replace('_', ' '))
            btn.setMinimumSize(350, 100)
            btn.setStyleSheet("font: 75 25pt; background-color: blue; color: white;")
            
            # Store the category ID as a property of the button
            btn.category_id = category_id
            btn.category_name = category_name
            
            self.categoryLayout.addWidget(btn, row, col)
            self.categoryButtons[category_id] = btn
            
            col += 1
            if col >= 3:
                col = 0
                row += 1

class SalesView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UIContainer()
        self.ui.setupUi(self)
        self.cart_items = {}
        self.setup_tables()
        self.connect_signals()

    def setup_tables(self):
        # Product table
        self.product_model = QStandardItemModel()
        self.product_model.setHorizontalHeaderLabels(['Name', 'SKU', 'Selling Price', 'Quantity', 'Add'])
        self.ui.productTable.setModel(self.product_model)
        
        # Cart table
        self.cart_model = QStandardItemModel()
        self.cart_model.setHorizontalHeaderLabels(['Item', 'Qty', 'Price', 'Delete'])
        self.ui.cartList.setModel(self.cart_model)

    def connect_signals(self):
        # Connect category buttons
        for btn in self.ui.categoryButtons.values():
            btn.clicked.connect(lambda checked, b=btn: self.load_products(b.category_name))
        # Connect search
        self.ui.skuSearch.textChanged.connect(self.filter_products)
        
        # Connect cart interactions
        #self.ui.productTable.doubleClicked.connect(self.add_to_cart)
        self.ui.discountValue.valueChanged.connect(self.update_totals)
        self.ui.payButton.clicked.connect(self.process_payment)

    def load_products(self, category):
        query = QSqlQuery()
        query.prepare("SELECT name, sku, sell_price, qty FROM products WHERE category_id = (SELECT id FROM categories WHERE name = ?)")
        query.addBindValue(category)
        query.exec_()
        
        self.product_model.setRowCount(0)
        while query.next():
            row = []
            for i in range(4):
                item = QStandardItem(str(query.value(i)))
                row.append(item)
            
            # Add empty item for the Add button column
            row.append(QStandardItem(""))
            self.product_model.appendRow(row)
            
            # Create and add the Add button
            addBtn = QPushButton("+")
            addBtn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
            addBtn.clicked.connect(lambda checked, r=self.product_model.rowCount()-1: self.add_to_cart_from_button(r))
            self.ui.productTable.setIndexWidget(
                self.product_model.index(self.product_model.rowCount()-1, 4),
                addBtn
            )

    def add_to_cart_from_button(self, row):
        sku = self.product_model.item(row, 1).text()
        name = self.product_model.item(row, 0).text()
        price = float(self.product_model.item(row, 2).text())
        
        if sku in self.cart_items:
            self.cart_items[sku]['qty'] += 1
        else:
            self.cart_items[sku] = {
                'name': name,
                'qty': 1,
                'price': price
            }
        
        self.update_cart_display()

    def add_to_cart(self, index):
        row = index.row()
        sku = self.product_model.item(row, 1).text()
        name = self.product_model.item(row, 0).text()
        price = float(self.product_model.item(row, 2).text())
        
        if sku in self.cart_items:
            self.cart_items[sku]['qty'] += 1
        else:
            self.cart_items[sku] = {
                'name': name,
                'qty': 1,
                'price': price
            }
        
        self.update_cart_display()

    def filter_products(self, text):
        model = self.ui.productTable.model()
        for row in range(model.rowCount()):
            sku = model.index(row, 1).data()
            self.ui.productTable.setRowHidden(row, not text.lower() in str(sku).lower())


    def update_quantity(self, index):
        row = index.row()
        if row >= len(self.cart_items):
            return
            
        key = list(self.cart_items.keys())[row]
        quantity, ok = QInputDialog.getInt(
            self, 'Update Quantity', 
            'Enter quantity:', 
            self.cart_items[key]['qty'], 
            0, 100, 1
        )
        
        if ok:
            if quantity == 0:
                del self.cart_items[key]
            else:
                self.cart_items[key]['qty'] = quantity
                item_total = self.cart_items[key]['price'] * quantity
                self.cart_items[key]['total'] = item_total
            self.update_cart_display()

    def update_cart_display(self):
        self.cart_model.setRowCount(0)
        total = 0
        
        for sku, item in self.cart_items.items():
            row = []
            item_subtotal = item['price'] * item['qty']
            total += item_subtotal
            
            row.append(QStandardItem(item['name']))
            
            # Create QLineEdit for quantity
            qtyEdit = QLineEdit()
            qtyEdit.setText(str(item['qty']))
            qtyEdit.setStyleSheet("background-color: #3b3b3b; color: white;")
            # Validate input to only accept numbers
            qtyEdit.setValidator(QIntValidator(0, 999))
            # Connect the editing finished signal
            qtyEdit.editingFinished.connect(lambda sku=sku, edit=qtyEdit: self.update_item_quantity(sku, edit))
            
            row.append(QStandardItem(""))  # Empty item for qty column
            row.append(QStandardItem(f"${item['price']:.2f}"))
            
            deleteBtn = QPushButton("×")
            deleteBtn.clicked.connect(lambda checked, s=sku: self.remove_item(s))
            deleteBtn.setStyleSheet("background-color: red; color: white;")
            
            self.cart_model.appendRow(row)
            
            # Set the QLineEdit widget in the quantity column
            self.ui.cartList.setIndexWidget(
                self.cart_model.index(self.cart_model.rowCount()-1, 1),
                qtyEdit
            )
            
            # Set the delete button
            self.ui.cartList.setIndexWidget(
                self.cart_model.index(self.cart_model.rowCount()-1, 3),
                deleteBtn
            )

        self.ui.subTotalValue.setText(f"{total:.2f}")
        self.update_totals()

    def update_item_quantity(self, sku, qtyEdit):
        try:
            new_qty = int(qtyEdit.text())
            if new_qty <= 0:
                self.remove_item(sku)
            else:
                self.cart_items[sku]['qty'] = new_qty
                self.update_cart_display()
        except ValueError:
            # Reset to previous value if invalid input
            qtyEdit.setText(str(self.cart_items[sku]['qty']))

    def calculate_total(self):
        subtotal = float(self.ui.sub_total.text().replace('$', ''))
        discount = float(self.ui.discount.text() or 0)
        final_total = subtotal - discount
        self.ui.total_payment.setText(f"${final_total:.2f}")


    def update_totals(self):
        subtotal = float(self.ui.subTotalValue.text())
        discount = int(self.ui.discountValue.text() or 0)
        final_total = subtotal - discount
        self.ui.totalValue.setText(f"{final_total:.2f}")

    def remove_item(self, sku):
        if sku in self.cart_items:
            del self.cart_items[sku]
            self.update_cart_display()

    def process_payment(self):
        try:
            # Get all the payment details
            payment_data = {
                'items': [
                    {
                        'sku': sku,
                        'name': item['name'],
                        'quantity': item['qty'],
                        'price': item['price'],
                        'subtotal': item['price'] * item['qty']
                    }
                    for sku, item in self.cart_items.items()
                ],
                'subtotal': float(self.ui.subTotalValue.text()),
                'discount': float(self.ui.discountValue.text() or 0),
                'total': float(self.ui.totalValue.text()),
                'paid_amount': float(self.ui.paidInput.text() or 0),
                'balance': float(self.ui.balanceInput.text() or 0),
                'timestamp': QDateTime.currentDateTime().toString(Qt.ISODate)
            }


            if not self.update_inventory_after_sale():
                return

            # Convert payment data to JSON string
            payment_json = json.dumps(payment_data)

            # Save to database
            query = QSqlQuery()
            query.prepare("""
                INSERT INTO payments (payment_data, created_at)
                VALUES (?, CURRENT_TIMESTAMP)
            """)
            query.addBindValue(payment_json)

            if query.exec_():
                QMessageBox.information(self, "Success", "Payment processed successfully!")
                # Clear the cart and reset the form
                self.cart_items = {}
                self.update_cart_display()
                self.ui.paidInput.clear()
                self.ui.balanceInput.clear()

                receipt_window = ReceiptView(payment_data, self)
                receipt_window.exec_()
            else:
                QMessageBox.critical(self, "Error", "Failed to process payment: " + query.lastError().text())

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def update_inventory_after_sale(self):
        try:
            # Start a transaction
            query = QSqlQuery()
            if not query.exec_("BEGIN TRANSACTION"):
                raise Exception("Failed to start transaction")

            # Update quantities for each item in the cart
            for sku, item in self.cart_items.items():
                update_query = QSqlQuery()
                update_query.prepare("""
                    UPDATE products 
                    SET qty = qty - ? 
                    WHERE sku = ? AND qty >= ?
                """)
                update_query.addBindValue(item['qty'])
                update_query.addBindValue(sku)
                update_query.addBindValue(item['qty'])

                if not update_query.exec_():
                    raise Exception(f"Failed to update quantity for SKU {sku}: {update_query.lastError().text()}")

                # Check if any rows were affected
                if update_query.numRowsAffected() == 0:
                    # Check if it failed because of insufficient quantity
                    check_query = QSqlQuery()
                    check_query.prepare("SELECT qty FROM products WHERE sku = ?")
                    check_query.addBindValue(sku)
                    check_query.exec_()
                    
                    if check_query.next():
                        current_qty = check_query.value(0)
                        raise Exception(f"Insufficient quantity for {item['name']} (SKU: {sku}). Available: {current_qty}")
                    else:
                        raise Exception(f"Product not found: {sku}")

            # If we get here, all updates were successful
            if not query.exec_("COMMIT"):
                raise Exception("Failed to commit transaction")
            
            return True

        except Exception as e:
            # Roll back the transaction if any error occurred
            query.exec_("ROLLBACK")
            QMessageBox.critical(self, "Inventory Update Error", str(e))
            return False            