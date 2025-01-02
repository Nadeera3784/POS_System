from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QTableView, QHeaderView, QDateEdit, QDialog, QTextEdit, QLineEdit)
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDate
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel
import json
from datetime import datetime, timedelta
from Application.Components.Reports.PaymentDetails import PaymentDetails

class ReportsView(QWidget):
    def __init__(self, parent=None):
        super(ReportsView, self).__init__(parent)
        self.db = self.initialize_database()
        self.layout = QVBoxLayout()
        
        # Date Filter Section
        self.filter_layout = QHBoxLayout()
        
        # Start Date
        start_date_layout = QHBoxLayout()
        start_date_layout.addWidget(QLabel("Start Date:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        start_date_layout.addWidget(self.start_date)
        
        # End Date
        end_date_layout = QHBoxLayout()
        end_date_layout.addWidget(QLabel("End Date:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        end_date_layout.addWidget(self.end_date)
        
        # Filter Buttons
        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.apply_date_filter)
        
        self.clear_filter_btn = QPushButton("Clear Filters")
        self.clear_filter_btn.clicked.connect(self.clear_date_filter)
        
        # Add to filter layout
        self.filter_layout.addLayout(start_date_layout)
        self.filter_layout.addLayout(end_date_layout)
        self.filter_layout.addWidget(self.apply_filter_btn)
        self.filter_layout.addWidget(self.clear_filter_btn)
        self.filter_layout.addStretch()
        
        self.layout.addLayout(self.filter_layout)
        
        # Table Setup
        self.queryModel = QSqlQueryModel()
        self.tableView = QTableView()
        self.tableView.setModel(self.queryModel)
        self.tableView.setSortingEnabled(True)
        self.tableView.doubleClicked.connect(self.show_payment_details)
        self.tableView.setMinimumHeight(500)  # Set minimum height for the table
        self.layout.addWidget(self.tableView)
        
        # Pagination Controls
        self.currentPage = 1
        self.pageRecordCount = 20
        self.totalPage = None
        self.totalRecordCount = None
        
        # Add pagination at the bottom
        self.setup_pagination_controls()
        self.initialize_table()
        self.setup_connections()
        
        self.setLayout(self.layout)

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

    def setup_pagination_controls(self):
        # Pagination Controls
        self.totalPageLabel = QLabel()
        self.currentPageLabel = QLabel()
        self.switchPageLineEdit = QLineEdit()
        self.prevButton = QPushButton("Previous")
        self.nextButton = QPushButton("Next")
        self.switchPageButton = QPushButton("Go to Page")
        
        # Create pagination layout
        pagination_layout = QHBoxLayout()
        
        # Left side - Previous/Next buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prevButton)
        button_layout.addWidget(self.nextButton)
        pagination_layout.addLayout(button_layout)
        
        # Center - Page navigation
        page_nav_layout = QHBoxLayout()
        page_nav_layout.addWidget(QLabel("Go to page:"))
        self.switchPageLineEdit.setFixedWidth(40)
        page_nav_layout.addWidget(self.switchPageLineEdit)
        page_nav_layout.addWidget(self.switchPageButton)
        pagination_layout.addLayout(page_nav_layout)
        
        # Right side - Page information and Total Amount
        page_info_layout = QHBoxLayout()
        page_info_layout.addWidget(QLabel("Current page:"))
        page_info_layout.addWidget(self.currentPageLabel)
        page_info_layout.addWidget(QLabel("Total pages:"))
        page_info_layout.addWidget(self.totalPageLabel)
        page_info_layout.addWidget(QLabel("  |  Total Amount:"))
        self.totalAmountLabel = QLabel()
        self.totalAmountLabel.setStyleSheet("font-weight: bold;")
        page_info_layout.addWidget(self.totalAmountLabel)
        pagination_layout.addLayout(page_info_layout)
        
        # Add stretch to keep everything aligned
        pagination_layout.addStretch()
        
        # Add pagination layout to the main layout at the bottom
        self.layout.addLayout(pagination_layout)

    def setup_connections(self):
        self.prevButton.clicked.connect(self.on_prev_page)
        self.nextButton.clicked.connect(self.on_next_page)
        self.switchPageButton.clicked.connect(self.on_switch_page)

    def initialize_table(self):
        if not self.db or not self.db.isOpen():
            self.db = self.initialize_database()

        # Get total record count and sum
        count_query = QSqlQuery()
        count_query.exec_("""
            SELECT 
                COUNT(*),
                SUM(CAST(json_extract(payment_data, '$.total') AS FLOAT))
            FROM payments
        """)
        if count_query.next():
            self.totalRecordCount = count_query.value(0)
            self.totalAmount = count_query.value(1) or 0.0
            self.totalPage = (self.totalRecordCount + self.pageRecordCount - 1) // self.pageRecordCount

        # Initial query
        self.query_records(0)
        self.update_pagination_status()

    def query_records(self, offset):
        sql = f"""
            SELECT 
                id as ID,
                created_at as 'Transaction Date',
                json_extract(payment_data, '$.total') as 'Total Amount',
                json_extract(payment_data, '$.paid_amount') as 'Paid Amount',
                json_extract(payment_data, '$.balance') as 'Balance'
            FROM payments 
            LIMIT {self.pageRecordCount} 
            OFFSET {offset}
        """
        self.queryModel.setQuery(sql)
        
        # Set headers
        self.queryModel.setHeaderData(0, Qt.Horizontal, "ID")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "Transaction Date")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "Total Amount")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "Paid Amount")
        self.queryModel.setHeaderData(4, Qt.Horizontal, "Balance")
        
        # Adjust column widths
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def apply_date_filter(self):
        start_date = self.start_date.date().toString(Qt.ISODate)
        end_date = self.end_date.date().toString(Qt.ISODate)
        
        # Update total record count and sum with filter
        count_query = QSqlQuery()
        count_query.prepare("""
            SELECT 
                COUNT(*),
                SUM(CAST(json_extract(payment_data, '$.total') AS FLOAT))
            FROM payments 
            WHERE date(created_at) BETWEEN date(?) AND date(?)
        """)
        count_query.addBindValue(start_date)
        count_query.addBindValue(end_date)
        count_query.exec_()
        
        if count_query.next():
            self.totalRecordCount = count_query.value(0)
            self.totalAmount = count_query.value(1) or 0.0
            self.totalPage = (self.totalRecordCount + self.pageRecordCount - 1) // self.pageRecordCount
            self.currentPage = 1
        
        # Apply filter to table
        sql = f"""
            SELECT 
                id as ID,
                created_at as 'Transaction Date',
                json_extract(payment_data, '$.total') as 'Total Amount',
                json_extract(payment_data, '$.paid_amount') as 'Paid Amount',
                json_extract(payment_data, '$.balance') as 'Balance'
            FROM payments 
            WHERE date(created_at) BETWEEN date('{start_date}') AND date('{end_date}')
            LIMIT {self.pageRecordCount} 
            OFFSET {(self.currentPage - 1) * self.pageRecordCount}
        """
        self.queryModel.setQuery(sql)
        self.update_pagination_status()

    def show_payment_details(self, index):
        # Get the payment ID from the selected row
        row = index.row()
        payment_id = self.queryModel.record(row).value("ID")
        
        # Query the full payment data
        query = QSqlQuery()
        query.prepare("SELECT payment_data FROM payments WHERE id = ?")
        query.addBindValue(payment_id)
        query.exec_()
        
        if query.next():
            payment_data = query.value(0)
            dialog = PaymentDetails(payment_data, self)
            dialog.exec_()

    def on_prev_page(self):
        if self.currentPage > 1:
            self.currentPage -= 1
            self.query_records((self.currentPage - 1) * self.pageRecordCount)
            self.update_pagination_status()

    def on_next_page(self):
        if self.currentPage < self.totalPage:
            self.currentPage += 1
            self.query_records((self.currentPage - 1) * self.pageRecordCount)
            self.update_pagination_status()

    def on_switch_page(self):
        try:
            page = int(self.switchPageLineEdit.text())
            if 1 <= page <= self.totalPage:
                self.currentPage = page
                self.query_records((self.currentPage - 1) * self.pageRecordCount)
                self.update_pagination_status()
        except ValueError:
            pass

    def clear_date_filter(self):
        # Reset date controls to default values
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate())
        
        # Reset the table to show all records
        self.currentPage = 1
        self.initialize_table()
        
    def update_pagination_status(self):
        self.currentPageLabel.setText(str(self.currentPage))
        self.totalPageLabel.setText(str(self.totalPage))
        self.totalAmountLabel.setText(f"${self.totalAmount:.2f}")
        
        self.prevButton.setEnabled(self.currentPage > 1)
        self.nextButton.setEnabled(self.currentPage < self.totalPage)
        
        self.switchPageLineEdit.setText(str(self.currentPage))