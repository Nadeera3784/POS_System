from PyQt5.QtWidgets import (QTabWidget, QCalendarWidget)
import PyQt5.QtCore as QtCore

class ReportsView(QCalendarWidget):
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