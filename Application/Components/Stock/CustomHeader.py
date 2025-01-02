from PyQt5.QtWidgets import *
import PyQt5.QtCore as QtCore
from Application.Components.Stock.CustomHeaderModel import CustomHeaderModel

class CustomHeader(QHeaderView):
    def __init__(self, header,labels, parent= None):
        super().__init__(QtCore.Qt.Horizontal, parent) 
        self.main_header = header
        self.setModel(CustomHeaderModel(labels))
        self.sectionResized.connect(self.updateSizes)
        self.main_header.sectionResized.connect(self.updateSizes)
        self.setGeometry(0, 0, header.width(), header.height())
        
        # Configure header behavior
        self.setSectionsClickable(True)
        self.setSectionsMovable(True)
        self.setStretchLastSection(True)
        self.setSectionResizeMode(QHeaderView.Interactive)
        

    def updateSizes(self):
        for i in range(self.count()):
            self.resizeSection(i, self.main_header.sectionSize(i))
    
    def updateOffset(self):
        self.setOffset(self.main_header.offset())
        
    
    def eventFilter(self, object, event):
        if object == self.main_header:
            if event.type() == QtCore.QEvent.Resize:
                self.setOffset(self.main_header.offset())
                self.setGeometry(0, 0, self.main_header.width(), self.main_header.height())
            return False
        return super().eventFilter(object, event)

    def getSectionSizes(self, first,  second):
        size = 0
        for a in range(first, second + 1):
            size += self.main_header.sectionSize(a)
        return size
