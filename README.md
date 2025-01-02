# Point of Sale (POS) System 

A comprehensive retail management system developed using Python and PyQt5, designed to streamline point-of-sale operations, inventory management, and business analytics. The solution provides enterprise-grade functionality while maintaining a user-friendly interface suitable for diverse retail environments.


## Features

### Administrative Dashboard(Dashboard)

![Preview](https://raw.githubusercontent.com/Nadeera3784/POS_System/master/Data/dashboard.png)
- Key performance indicators 
- Low stock alert table

### Inventory Control System (Stock)

![Preview](https://raw.githubusercontent.com/Nadeera3784/POS_System/master/Data/stock.png)

- Centralized product database with full CRUD functionality
- Multi-parameter search capabilities with SKU-based tracking
- Category-driven organization system
- Purchase price and selling price management
- Batch update capabilities for efficient inventory maintenance


### Transaction Processing Module(Sales)

![Preview](https://raw.githubusercontent.com/Nadeera3784/POS_System/master/Data/sales.png)

- Real-time sales processing with intuitive category-based product selection
- Dynamic cart management with automated price calculations
- Flexible discount application system
- Advanced payment processing with balance computation
- Professional receipt generation and multi-format printing capabilities
- Configurable tax and pricing rules


### Financial Reporting Engine(Reports)

![Preview](https://raw.githubusercontent.com/Nadeera3784/POS_System/master/Data/reports.png)

- Comprehensive transaction history tracking
- Customizable date-range analytics
- Detailed payment reconciliation
- Advanced filtering and sorting capabilities
- Aggregated financial summaries
- Exportable report generation


### Technical Architecture:

- Frontend: PyQt5 framework
- Backend: SQLite database with optimized query handling
- Custom delegate system for enhanced table interactions
- Modular design enabling seamless feature extensions
- Robust error handling and data validation
- Print subsystem supporting multiple output formats


### Installation

POS system requires python v3.9.6+ and PyQt5 to run.

> Needs to run migrate.py to create databases.

```sh
python migrate.py
```


```sh
python run.py
```

> Username : john  
> Password : 1234  