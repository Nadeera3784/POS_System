from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit, QMessageBox, QWidget, QMainWindow, QAction, QTabWidget,
QVBoxLayout, QFrame, QSplitter,QStyleFactory, QTableView, QHeaderView, QStackedLayout)
import PyQt5.QtCore as QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import sys, random
from datetime import datetime

from Application.Components.Stock.View import StockView
from Application.Components.Sales.View import SalesView
from Application.Components.Reports.View import ReportsView


class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('POS System v.1.0')
        self.setObjectName("DashboardView")
        self._widget = QWidget()
        self._layout = QVBoxLayout(self._widget)
        self._widget.setLayout(self._layout);
        self.dashboard_label = QLabel("Dashboard")
        self.tabwidget = QTabWidget()
        self.dashboard_widget = self.initUI()
        self.tabwidget.addTab(self.dashboard_widget, "Dashboard")
        self.stock_widget = StockView()
        self.tabwidget.addTab(self.stock_widget, "Stock")   
        self.sales_widget = SalesView()
        self.tabwidget.addTab(self.sales_widget, "Sales")
        self.reports_widget =  ReportsView()
        self.tabwidget.addTab(self.reports_widget, "Reports")
        self._layout.addWidget(self.tabwidget)
        self.setCentralWidget(self._widget)


    def get_current_month_stats(self):
        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("Data/database.db")
        if not db.isOpen():
            db.open()
        
        query = QSqlQuery()
        current_month = datetime.now().strftime('%Y-%m')
        
        # Get total sales for current month
        query.prepare("""
                SELECT COALESCE(SUM(CAST(JSON_EXTRACT(payment_data, '$.total') AS FLOAT)), 0) as total_sales
                FROM payments 
                WHERE strftime('%Y-%m', created_at) = ?
            """)
        query.addBindValue(current_month)
        query.exec_()
        total_sales = 0
        if query.next():
            total_sales = query.value(0)

        # Get total profit for current month
        query.prepare("""
            WITH RECURSIVE 
            json_items AS (
                SELECT 
                    p.id,
                    json_extract(value, '$.sku') as sku,
                    CAST(json_extract(value, '$.quantity') AS INTEGER) as sold_qty,
                    CAST(json_extract(value, '$.price') AS DECIMAL) as selling_price
                FROM payments p,
                json_each(json_extract(p.payment_data, '$.items'))
                WHERE strftime('%Y-%m', p.created_at) = ?
            )
            SELECT COALESCE(
                SUM(
                    (ji.selling_price - pr.purchase_price) * ji.sold_qty
                ), 0
            ) as total_profit
            FROM json_items ji
            JOIN products pr ON pr.sku = ji.sku
        """)
        query.addBindValue(current_month)
        query.exec_()
        total_profit = 0
        if query.next():
            total_profit = query.value(0)

        # Get total number of products
        query.exec_("SELECT COUNT(*) FROM products")
        total_products = 0
        if query.next():
            total_products = query.value(0)

        return total_sales, total_profit, total_products

    def initUI(self):
        self.widgetContainer = QWidget(self)
        self.widgetContainerLayout = QHBoxLayout()
        self.widgetStatisticsLayout = QVBoxLayout()
        self.widgetStatisticsLayout.addLayout(self.widgetContainerLayout)

        # Get real statistics
        total_sales, total_profit, total_products = self.get_current_month_stats()
        
        # Sales Box
        self.SalesBox = QGroupBox("Monthly Sales")
        self.SalesBoxLayout = QHBoxLayout(self.SalesBox)
        self.SalesBox.setLayout(self.SalesBoxLayout)
        self.SalesBoxData = QLabel(f"${total_sales:,.2f}")
        self.SalesBoxData.setStyleSheet("font: 75 35pt; color: black;")
        self.SalesBoxData.setMargin(15)
        self.SalesBoxData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.SalesBoxLayout.addWidget(self.SalesBoxData)

        # Profit Box
        self.ProfitBox = QGroupBox("Monthly Profit")
        self.ProfitBoxLayout = QHBoxLayout(self.ProfitBox)
        self.ProfitBox.setLayout(self.ProfitBoxLayout)
        self.ProfitBoxData = QLabel(f"${total_profit:,.2f}")
        self.ProfitBoxData.setStyleSheet("font: 75 35pt; color: black;")
        self.ProfitBoxData.setMargin(15)
        self.ProfitBoxData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.ProfitBoxLayout.addWidget(self.ProfitBoxData)

        # Products Box
        self.ProductsBox = QGroupBox("Total Products")
        self.ProductsBoxLayout = QHBoxLayout(self.ProductsBox)
        self.ProductsBox.setLayout(self.ProductsBoxLayout)
        self.ProductsBoxData = QLabel(str(total_products))
        self.ProductsBoxData.setStyleSheet("font: 75 35pt; color: black;")
        self.ProductsBoxData.setMargin(15)
        self.ProductsBoxData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.ProductsBoxLayout.addWidget(self.ProductsBoxData)

        # Add boxes to layout
        self.widgetContainerLayout.addWidget(self.SalesBox)
        self.widgetContainerLayout.addWidget(self.ProfitBox)
        self.widgetContainerLayout.addWidget(self.ProductsBox)

        self.lowStockGroup = QGroupBox("Low Stock Alert (Products with Qty ≤ 5)")
        self.lowStockLayout = QVBoxLayout()

         # Create table for low stock items
        self.lowStockTable = QTableView()
        self.lowStockTable.horizontalHeader().setStretchLastSection(True)
        self.lowStockTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lowStockTable.setEditTriggers(QTableView.NoEditTriggers)


        # Create and set up the model
        self.modelLowStock = QSqlQueryModel()
        self.update_low_stock_table()
        self.lowStockTable.setModel(self.modelLowStock)
        
        # Add to layout
        self.lowStockLayout.addWidget(self.lowStockTable)
        self.lowStockGroup.setLayout(self.lowStockLayout)
        self.widgetStatisticsLayout.addWidget(self.lowStockGroup)

        # Set up refresh button
        self.refreshButton = QPushButton("Refresh Data")
        self.refreshButton.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.refreshButton.clicked.connect(self.refresh_dashboard)
        self.widgetStatisticsLayout.addWidget(self.refreshButton)

        self.widgetContainer.setLayout(self.widgetStatisticsLayout)

        return self.widgetContainer

    def update_low_stock_table(self):
        """Update the low stock table data"""
        query = """
            SELECT name as 'Product Name', 
                sku as 'SKU', 
                qty as 'Current Quantity',
                sell_price as 'Selling Price'
            FROM products 
            WHERE qty <= 5
            ORDER BY qty ASC
        """
        self.modelLowStock.setQuery(query)


    def refresh_dashboard(self):
        total_sales, total_profit, total_products = self.get_current_month_stats()
        self.SalesBoxData.setText(f"${total_sales:,.2f}")
        self.ProfitBoxData.setText(f"${total_profit:,.2f}")
        self.ProductsBoxData.setText(str(total_products))
        
        # Refresh low stock table
        self.update_low_stock_table()




