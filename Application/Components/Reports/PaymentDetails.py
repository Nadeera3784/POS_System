from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QDateEdit, QDialog, QTextEdit)
import json

class PaymentDetails(QDialog):
    def __init__(self, payment_data, parent=None):
        super().__init__(parent)
        self.payment_data = payment_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Payment Details")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Create details content
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        # Parse the payment data JSON
        payment_info = json.loads(self.payment_data)
        
        # Generate details HTML
        details_html = f"""
        <div style='font-family: Arial; width: 100%;'>
            <h2 style='text-align: center;'>Payment Details</h2>
            <p style='text-align: center;'>{payment_info['timestamp']}</p>
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
        for item in payment_info['items']:
            details_html += f"""
                <tr>
                    <td>{item['name']}</td>
                    <td style='text-align: right;'>{item['quantity']}</td>
                    <td style='text-align: right;'>${item['price']:.2f}</td>
                    <td style='text-align: right;'>${item['subtotal']:.2f}</td>
                </tr>
            """
            
        # Add totals
        details_html += f"""
            </table>
            <hr>
            <table width='100%'>
                <tr>
                    <td style='text-align: right;'>Subtotal:</td>
                    <td style='text-align: right; width: 100px;'>${payment_info['subtotal']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Discount:</td>
                    <td style='text-align: right;'>${payment_info['discount']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'><b>Total:</b></td>
                    <td style='text-align: right;'><b>${payment_info['total']:.2f}</b></td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Paid Amount:</td>
                    <td style='text-align: right;'>${payment_info['paid_amount']:.2f}</td>
                </tr>
                <tr>
                    <td style='text-align: right;'>Balance:</td>
                    <td style='text-align: right;'>${payment_info['balance']:.2f}</td>
                </tr>
            </table>
        </div>
        """
        
        self.details_text.setHtml(details_html)
        layout.addWidget(self.details_text)
        
        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
