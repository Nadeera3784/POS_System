from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QDialog, QTextEdit)
from PyQt5.QtCore import QDateTime, Qt, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

class ReceiptView(QDialog):
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
