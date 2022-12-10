import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re


class Ui_Form(QObject):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        #Form.resize(1500, 900)
        #Form.setMinimumSize(QtCore.QSize(1500, 900))
        #Form.setMaximumSize(QtCore.QSize(1500, 900))
        Form.setWindowTitle("Sales")

        self.layoutWidget01 = QtWidgets.QWidget(Form)
        self.layoutWidget01.setGeometry(QtCore.QRect(0, 0, 1200, 100))
        self.layoutWidget01.setObjectName("layoutWidget01")
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout(self.layoutWidget01)
        self.horizontalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")

        self.sortByChickenBtn = QtWidgets.QPushButton(self.layoutWidget01)
        self.sortByChickenBtn.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByChickenBtn.setObjectName("sortByChickenBtn")
        self.sortByChickenBtn.setText("Chicken")
        self.horizontalLayout_1.addWidget(self.sortByChickenBtn)

        self.sortByDrinkBtn = QtWidgets.QPushButton(self.layoutWidget01)
        self.sortByDrinkBtn.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByDrinkBtn.setObjectName("sortByDrinkBtn")
        self.sortByDrinkBtn.setText("Drink")
        self.horizontalLayout_1.addWidget(self.sortByDrinkBtn)

        self.sortByOtherBtn = QtWidgets.QPushButton(self.layoutWidget01)
        self.sortByOtherBtn.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByOtherBtn.setObjectName("sortByOtherBtn")
        self.sortByOtherBtn.setText("Other")
        self.horizontalLayout_1.addWidget(self.sortByOtherBtn)

        self.layoutWidget_2 = QtWidgets.QWidget(Form)
        self.layoutWidget_2.setGeometry(QtCore.QRect(0, 110, 1200, 100))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.sortByChickenBtn_2 = QtWidgets.QPushButton(self.layoutWidget_2)
        self.sortByChickenBtn_2.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn_2.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn_2.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByChickenBtn_2.setObjectName("sortByChickenBtn_2")
        self.sortByChickenBtn_2.setText("HP")
        self.horizontalLayout_2.addWidget(self.sortByChickenBtn_2)

        self.sortByDrinkBtn_2 = QtWidgets.QPushButton(self.layoutWidget_2)
        self.sortByDrinkBtn_2.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn_2.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn_2.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByDrinkBtn_2.setObjectName("sortByDrinkBtn_2")
        self.sortByDrinkBtn_2.setText("Apple")
        self.horizontalLayout_2.addWidget(self.sortByDrinkBtn_2)

        self.sortByOtherBtn_2 = QtWidgets.QPushButton(self.layoutWidget_2)
        self.sortByOtherBtn_2.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn_2.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn_2.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByOtherBtn_2.setObjectName("sortByOtherBtn_2")
        self.sortByOtherBtn_2.setText("Nokia")
        self.horizontalLayout_2.addWidget(self.sortByOtherBtn_2)



        self.layoutWidget_3 = QtWidgets.QWidget(Form)
        self.layoutWidget_3.setGeometry(QtCore.QRect(0, 220, 1200, 100))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.sortByChickenBtn_3 = QtWidgets.QPushButton(self.layoutWidget_3)
        self.sortByChickenBtn_3.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn_3.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByChickenBtn_3.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByChickenBtn_3.setObjectName("sortByChickenBtn_3")
        self.sortByChickenBtn_3.setText("Samsung")
        self.horizontalLayout_3.addWidget(self.sortByChickenBtn_3)

        self.sortByDrinkBtn_3 = QtWidgets.QPushButton(self.layoutWidget_3)
        self.sortByDrinkBtn_3.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn_3.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByDrinkBtn_3.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByDrinkBtn_3.setObjectName("sortByDrinkBtn_3")
        self.sortByDrinkBtn_3.setText("Lenavo")
        self.horizontalLayout_3.addWidget(self.sortByDrinkBtn_3)

        self.sortByOtherBtn_3 = QtWidgets.QPushButton(self.layoutWidget_3)
        self.sortByOtherBtn_3.setMinimumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn_3.setMaximumSize(QtCore.QSize(400, 100))
        self.sortByOtherBtn_3.setStyleSheet("font: 75 35pt;  background-color: #2D55DB; color: #fff;")
        self.sortByOtherBtn_3.setObjectName("sortByOtherBtn_3")
        self.sortByOtherBtn_3.setText("Dell")
        self.horizontalLayout_3.addWidget(self.sortByOtherBtn_3)

        self.layoutWidget_4 = QtWidgets.QWidget(Form)
        self.layoutWidget_4.setGeometry(QtCore.QRect(0, 330, 1200, 20))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.top_box_layout = QtWidgets.QHBoxLayout(self.layoutWidget_4)
        self.top_box_layout.setContentsMargins(0, 0, 0, 0)
        self.add_button = QtWidgets.QPushButton("Add +")
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("SKU");
        self.search_button = QtWidgets.QPushButton("Search")
        self.top_box_layout.addWidget(self.add_button)
        self.top_box_layout.addWidget(self.search_box)
        self.top_box_layout.addWidget(self.search_button)


        self.layoutWidget_5 = QtWidgets.QWidget(Form)
        self.layoutWidget_5.setGeometry(QtCore.QRect(0, 360, 1200, 500))
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.horizontalLayout_5 = QtWidgets.QVBoxLayout(self.layoutWidget_5)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.orderList = QtWidgets.QTableView()
        self.orderList.setMinimumSize(QtCore.QSize(1200, 500))
        self.orderList.setMaximumSize(QtCore.QSize(1200, 500))
        self.orderList.setStyleSheet("font: 75 25pt \"함초롬돋움\";")
        self.orderList.setObjectName("orderList")
        self.orderList.verticalHeader().setVisible(False)
        self.orderList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.orderList.resizeColumnsToContents()
        self.header  = self.orderList.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignHCenter)
        self.horizontalLayout_5.addWidget(self.orderList)

        orderModel = QtGui.QStandardItemModel()
        orderModel.setHorizontalHeaderLabels(['No', 'Sku', 'Name', 'Price'])

        orderModel.setItem(0, 0, QtGui.QStandardItem('0'))
        orderModel.setItem(0, 1, QtGui.QStandardItem('9834938'))
        orderModel.setItem(0, 2, QtGui.QStandardItem('HP'))
        orderModel.setItem(0, 3, QtGui.QStandardItem('3343'))
        self.orderList.resizeColumnsToContents()
        self.orderList.setModel(orderModel)




        self.layoutWidget_6 = QtWidgets.QWidget(Form)
        self.layoutWidget_6.setGeometry(QtCore.QRect(1200, 0, 600, 700))
        self.layoutWidget_6.setObjectName("layoutWidget_6")
        self.horizontalLayout_6 = QtWidgets.QVBoxLayout(self.layoutWidget_6)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.productList = QtWidgets.QTableView()
        self.productList.setMinimumSize(QtCore.QSize(1200, 700))
        self.productList.setMaximumSize(QtCore.QSize(1200, 700))
        self.productList.setStyleSheet("font: 75 25pt \"함초롬돋움\";")
        self.productList.setObjectName("productList")
        self.productList.verticalHeader().setVisible(False)
        self.productList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.productList.resizeColumnsToContents()
        self.header  = self.productList.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignHCenter)
        self.horizontalLayout_6.addWidget(self.productList)

        proudctModel = QtGui.QStandardItemModel()
        proudctModel.setHorizontalHeaderLabels(['No', 'Sku', 'Name', 'Price'])

        proudctModel.setItem(0, 0, QtGui.QStandardItem('0'))
        proudctModel.setItem(0, 1, QtGui.QStandardItem('9834938'))
        proudctModel.setItem(0, 2, QtGui.QStandardItem('HP'))
        proudctModel.setItem(0, 3, QtGui.QStandardItem('3343'))
        self.productList.resizeColumnsToContents()
        self.productList.setModel(proudctModel)

        QtCore.QMetaObject.connectSlotsByName(Form)



class SalesView(QMainWindow, Ui_Form):
    def __init__(self, parent=None):
        super(SalesView, self).__init__(parent)
        self.setupUi(self)
        self.show()
    #def initUI(self):






