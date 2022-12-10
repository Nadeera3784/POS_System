from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit, QMessageBox, QWidget, QMainWindow,
QVBoxLayout)
import sys

from Application.Components.Dashboard import DashboardView

class Boot(QDialog):
    def __init__(self, parent=None):
        super(Boot, self).__init__(parent)
        self.createFormGroupBox()
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Login", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.buttonBox.accepted.connect(self.onClickLogin)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.formGroupBox)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)
        self.setWindowTitle("Login")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Login")
        self.layout = QFormLayout()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.username = QLineEdit()
        self.layout.addRow(QLabel("Username:"), self.username)
        self.password.setObjectName("password")
        self.layout.addRow(QLabel("Password:"), self.password)
        self.formGroupBox.setLayout(self.layout)

    def onClickLogin(self):
        ##if self.username.text() == "john" and self.password.text() == "1234":
        if self.username.text() == "":
           self.accept()
        else:
         self.msg = QMessageBox()
         self.msg.setText("Error")
         self.msg.setInformativeText('Incorrect username or password')
         self.msg.setWindowTitle("Sign In Error")
         self.msg.exec_()

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    bootUI = Boot()
    if bootUI.exec_() == QDialog.Accepted:
        main_window = DashboardView()
        main_window.show()
        sys.exit(app.exec_())
    #sys.exit(dialog.exec_())
