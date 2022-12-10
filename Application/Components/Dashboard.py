from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit, QMessageBox, QWidget, QMainWindow, QAction, QTabWidget,
QVBoxLayout, QFrame, QSplitter,QStyleFactory, QTableView, QHeaderView, QStackedLayout)
import PyQt5.QtCore as QtCore
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtGui import QPainter
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import sys, random


from Application.Components.Stock import StockView
from Application.Components.Sales import SalesView
from Application.Components.Reports import ReportsView


class DashboardView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('POS System v.1.1')
        self.setObjectName("DashboardView")
        #self.resize(860, 300)
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

    def initUI(self):
        self.widgetContainer = QWidget(self)
        self.widgetContainerLayout = QHBoxLayout()
        #self.widgetContainer.setLayout(self.widgetContainerLayout)
        self.widgetStatisticsLayout = QVBoxLayout()
        self.widgetStatisticsLayout.addLayout(self.widgetContainerLayout)
        self.SalesBox = QGroupBox("Sales")
        self.SalesBoxLayout = QHBoxLayout(self.SalesBox)
        self.SalesBox.setLayout(self.SalesBoxLayout)
        self.SalesBoxData = QLabel("1244")
        self.SalesBoxData.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.SalesBoxData.setMargin(30)
        self.SalesBoxData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.SalesBoxLayout.addWidget(self.SalesBoxData)
        self.Products = QGroupBox("Products")
        self.ProductsLayout = QHBoxLayout(self.Products)
        self.Products.setLayout(self.ProductsLayout)
        self.ProductsData = QLabel("1244")
        self.ProductsData.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.ProductsData.setMargin(30)
        self.ProductsData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.ProductsLayout.addWidget(self.ProductsData)
        self.Customers = QGroupBox("Customers")
        self.CustomersLayout = QHBoxLayout(self.Customers)
        self.Customers.setLayout(self.CustomersLayout)
        self.CustomersData = QLabel("1244")
        self.CustomersData.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.CustomersData.setMargin(30)
        self.CustomersData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.CustomersLayout.addWidget(self.CustomersData)
        self.Suppliers = QGroupBox("Suppliers")
        self.SuppliersLayout = QHBoxLayout(self.Suppliers)
        self.Suppliers.setLayout(self.SuppliersLayout)
        self.SuppliersData = QLabel("1244")
        self.SuppliersData.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.SuppliersData.setMargin(30)
        self.SuppliersData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.SuppliersLayout.addWidget(self.SuppliersData)
        self.Categories = QGroupBox("Categories")
        self.CategoriesLayout = QHBoxLayout(self.Categories)
        self.Categories.setLayout(self.CategoriesLayout)
        self.CategoriesData = QLabel("1244")
        self.CategoriesData.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.CategoriesData.setMargin(30)
        self.CategoriesData.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.CategoriesLayout.addWidget(self.CategoriesData)
        self.widgetContainerLayout.addWidget(self.SalesBox)
        self.widgetContainerLayout.addWidget(self.Products)
        self.widgetContainerLayout.addWidget(self.Customers)
        self.widgetContainerLayout.addWidget(self.Suppliers)
        self.widgetContainerLayout.addWidget(self.Categories)
        self.chart = self.generateChart()
        self.widgetStatisticsLayout.addWidget(self.chart)
        self.widgetContainer.setLayout(self.widgetStatisticsLayout)
        return self.widgetContainer;

    def generateChart(self):
        self.series = QLineSeries(self)
        self.series.append(0,6)
        self.series.append(2, 4)
        self.series.append(3, 8)
        self.series.append(7, 4)
        self.series.append(10, 5)
        self.series << QtCore.QPointF(11, 1) << QtCore.QPointF(13, 3) << QtCore.QPointF(17, 6) << QtCore.QPointF(18, 3) << QtCore.QPointF(20, 2)
        self.chart =  QChart()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.ChartTheme(QChart.ChartThemeBlueIcy)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTitle("Weekly Sales")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(QtCore.Qt.AlignBottom)
        self.chartview = QChartView(self.chart)
        self.chartview.setRenderHint(QPainter.Antialiasing)
        #self.setCentralWidget(self.chartview)
        return self.chartview; 

    def createDB(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("Data/database.db")
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







