import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5.QtWidgets import *
import re

class SalesUI(QWidget):
    def __init__(self, parent=None):
        super(SalesUI, self).__init__(parent)
        self.initUI()

    def initUI(self):
        # hbox = QHBoxLayout(self)
        # splitter_left = QSplitter(self)
        # splitter_left.setOrientation(QtCore.Qt.Horizontal)
        # left_frame = QFrame(splitter_left)
        # left_frame.setFrameShape(QFrame.StyledPanel)
        # left_frame.setStyleSheet("background-color: #c5e370") # left
        # left_frame.resize(300,300)

        # self.btn1 = QPushButton('btn1')
        # self.right_layout = QVBoxLayout()
        # self.right_layout.addWidget(self.btn1)
        # self.right_widget = QWidget()
        # self.right_widget.setLayout(self.right_layout)


        # splitter_left.addWidget(self.right_widget)



        # splitter_vertical = QSplitter(splitter_left)
        # sizePolicy = splitter_vertical.sizePolicy()
        # sizePolicy.setHorizontalStretch(1)


        # splitter_vertical.setSizePolicy(sizePolicy)
        # splitter_vertical.setOrientation(QtCore.Qt.Vertical)

        # top_frame = QFrame(splitter_vertical)
        # top_frame.setFrameShape(QFrame.StyledPanel)
        # top_frame.setStyleSheet("background-color: #d79fb1") # top


        # bottom_frame = QFrame(splitter_vertical)
        # bottom_frame.setFrameShape(QFrame.StyledPanel)
        # bottom_frame.setStyleSheet("background-color: rgb(200, 255, 255)") #bottom
        # hbox.addWidget(splitter_left)
        #self.setGeometry(500, 500, 750, 750)


        #-------------------------------------

        hbox = QHBoxLayout(self)

        topleft = QFrame(self)
        topleft.setFrameShape(QFrame.StyledPanel)

        topright = QFrame(self)
        topright.setFrameShape(QFrame.StyledPanel)

        bottom = QFrame(self)
        bottom.setFrameShape(QFrame.StyledPanel)

        splitter1 = QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)

        splitter2 = QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)
        self.setGeometry(300, 300, 450, 400)
        





