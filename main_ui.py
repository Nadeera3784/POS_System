from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit, QMessageBox, QWidget, QMainWindow, QAction, QTabWidget, QCalendarWidget,
QVBoxLayout, QFrame, QSplitter,QStyleFactory, QTableView, QHeaderView)
import PyQt5.QtCore as QtCore
#from PyQt5.QtGui import *
import sys, random
import stock_ui
import sales_ui

from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel

class Scheduler(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.events = {
            QtCore.QDate(2020, 10, 24): ["Bob's birthday"],
            QtCore.QDate(2020, 10, 19): ["Alice's birthday"]
        }
        #self.setGeometry(QtCore.QRect(0, 0, 331, 200))
        
    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        if date in self.events:
            painter.setBrush(QtCore.Qt.red)
            painter.drawEllipse(rect.topLeft() + QtCore.QPoint(12, 7), 3, 3)

class MainAppUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main UI')
        self.setObjectName("MainAppUI")
        self.resize(860, 300)
        #self.createDB()
        #self.scheduler = Scheduler()
        #self.scheduler.show()
        #self.centralwidget = QWidget(self)
        #self.centralwidget.setObjectName("centralwidget")
        #self.calendarWidget = QCalendarWidget(self.centralwidget)
        # self.calendarWidget.setGeometry(QtCore.QRect(0, 0, 331, 300))
        # self.calendarWidget.showToday();
        # self.calendarWidget.events = {
        #     QtCore.QDate(2020, 10, 8): ["Bob's birthday"],
        #     QtCore.QDate(2020, 10, 12): ["Alice's birthday"]
        # }

        # self.calendarWidget.setObjectName("calendarWidget")
        #self.setCentralWidget(self.centralwidget)


        #self.centralwidget = Scheduler()
        #self.centralwidget.show()
        #self.centralwidget.setObjectName("centralwidget")
        #self.setCentralWidget(self.centralwidget)


        self._widget = QWidget()
        self._layout = QVBoxLayout(self._widget)
        self._widget.setLayout(self._layout);
        #_cal = Scheduler()
        #_layout.addWidget(_cal)
        self.label1 = QLabel("Dashboard")
        self.label2 = QLabel("Stock")

        self.tabwidget = QTabWidget()

        self.tabwidget.addTab(self.label1, "Dashboard")
        
        self.stock_widget = stock_ui.StockUI()
        self.tabwidget.addTab(self.stock_widget, "Stock")   

        self.sales_widget = sales_ui.SalesUI()
        self.tabwidget.addTab(self.sales_widget, "Sales")


        self._layout.addWidget(self.tabwidget)

        self.setCentralWidget(self._widget)

    def init_ui():
    	print('hellow world')

    def createDB(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("database/database.db")
        if self.db.open():
            print("open DB success.")
            self.query = QSqlQuery()
            self.query.exec_("create table products(id INTEGER primary key, name varchar(100), sku varchar(10), qty int, sell_price int, purchase_price int)")
            self.query.exec_("insert into products values(NULL, 'Lifebuoy(100g)', '54745', 10, 53, 50)")
            self.query.exec_("insert into products values(NULL, 'Signal(70g)', '98765', 15,  80, 100)")
            self.query.exec_("insert into products values(NULL, 'Anchor(400g)', '09654', 10,  120, 550)")
            self.query.exec_("insert into products values(NULL, 'Vim(500ml)', '47484', 12, 215, 210)")
            self.query.exec_("insert into products values(NULL, 'Viva(400g)', '93848', 18, 332, 330)")
            self.query.exec_("insert into products values(NULL, 'Marmite(210g)', '36372', 5, 573, 570)")
            self.query.exec_("insert into products values(NULL, 'Laojee(400)', '09837', 17,  376, 374)")
            self.query.exec_("insert into products values(NULL, 'Samba rice', '12653', 22,  100, 97)")
            self.query.exec_("insert into products values(NULL, 'Watawala Tea(100g)', '44560',  25, 122, 120)")
            self.query.exec_("insert into products values(NULL, 'Maliban marie(330g)', '11232', 22, 147, 144)")
        self.db.close()







