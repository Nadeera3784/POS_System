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

class UIContainer(QObject):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowTitle("POS System v.1.1")
        Form.resize(1800, 900)

        # Menu Bar
        self.menuBar = QMenuBar(Form)
        for menu in ['Dashboard', 'Stock', 'Sales', 'Reports']:
            self.menuBar.addAction(menu)

        # Category Buttons Layout
        self.categoryLayout = QGridLayout()
        self.categories = [
            'Bakery', 'Beverages', 'Books',
            'Electronics', 'Health_Beauty', 'Household',
            'Stationery', 'Toys', 'Dell'
        ]
        
        for i, category in enumerate(self.categories):
            btn = QPushButton(category.replace('_', ' '))
            btn.setMinimumSize(350, 100)
            btn.setStyleSheet("font: 75 25pt; background-color: blue; color: white;")
            self.categoryLayout.addWidget(btn, i//3, i%3)

        # Product List Section
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
        Form.setMenuBar(self.menuBar)
        Form.setStyleSheet("background-color: #2b2b2b; color: white;")

    def calculate_balance(self):
        try:
            total = float(self.totalValue.text())
            paid = float(self.paidInput.text() or 0)
            balance = paid - total
            self.balanceInput.setText(f"{balance:.2f}")
        except ValueError:
            self.balanceInput.setText("Invalid input")

class ReceiptWindow(QDialog):
    def __init__(self, payment_data, parent=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Receipt Preview")
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Create receipt content
        self.receipt_text = QTextEdit()
        self.receipt_text.setReadOnly(True)
        
        # Generate receipt HTML
        receipt_html = f"""
        <div style='font-family: Arial; width: 100%;'>
            <h2 style='text-align: center;'>SALES RECEIPT</h2>
            <p style='text-align: center;'>{QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')}</p>
            <hr>
            <table width='100%' style='border-collapse: collapse;'>
                <tr>
                    <th style='text-align: left;'>Item</th>
                    <th style='text-align: right;'>Qty</th>
                    <th style='text-align: right;'>Price</th>
                    <th style='text-align: right;'>Subtotal</th>
                </tr>
        """
        
        # Add items
        for item in self.payment_data['items']:
            receipt_html += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td style='text-align: right;'>{item['quantity']}</td>
                    <td style='text-align: right;'>${item['price']:.2f}</td>
                    <td style='text-align: right;'>${item['subtotal']:.2f}</td>
                </tr>
            """
            
        # Add totals
        receipt_html += f"""
            </table>
            <hr>
            <table width='100%'>
                <tr>
                    <td style='text-align: right;'>Subtotal:</td>
                    <td style='text-align: right; width: 100px;'>${self.payment_data['subtotal']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Discount:</td>
                    <td style='text-align: right;'>${self.payment_data['discount']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'><b>Total:</b></td>
                    <td style='text-align: right;'><b>${self.payment_data['total']:.2f}</b></td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Paid Amount:</td>
                    <td style='text-align: right;'>${self.payment_data['paid_amount']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Balance:</td>
                    <td style='text-align: right;'>${self.payment_data['balance']:.2f}</td>
                </tr>
            </table>
            <hr>
            <p style='text-align: center;'>Thank you for your purchase!</p>
        </div>
        """
        
        self.receipt_text.setHtml(receipt_html)
        layout.addWidget(self.receipt_text)
        
        # Add print buttons
        button_layout = QHBoxLayout()
        
        print_button = QPushButton("Print")
        print_button.clicked.connect(self.print_receipt)
        
        preview_button = QPushButton("Print Preview")
        preview_button.clicked.connect(self.print_preview)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout.addWidget(print_button)
        button_layout.addWidget(preview_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def print_receipt(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QDialog.Accepted:
            self.receipt_text.print_(printer)
            
    def print_preview(self):
        printer = QPrinter()
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.receipt_text.print_(p))
        preview.exec_()

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
        for i, category in enumerate(self.ui.categories):
            button = self.ui.categoryLayout.itemAt(i).widget()
            button.clicked.connect(lambda c, cat=category: self.load_products(cat))
        
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

                receipt_window = ReceiptWindow(payment_data, self)
                receipt_window.exec_()
            else:
                QMessageBox.critical(self, "Error", "Failed to process payment: " + query.lastError().text())

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")