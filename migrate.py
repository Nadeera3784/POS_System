import os
import sqlite3
from datetime import datetime

class DatabaseMigration:
    def __init__(self, db_path="Data/database.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        
    def ensure_data_directory(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    def create_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    sku VARCHAR(20) NOT NULL UNIQUE,
                    qty INTEGER NOT NULL DEFAULT 0,
                    sell_price DECIMAL(10,2) NOT NULL,
                    purchase_price DECIMAL(10,2) NOT NULL,
                    category_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            ''')
            
            # Create payments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(created_at)')
            
            # Create triggers for updated_at timestamps
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
                    AFTER UPDATE ON products
                BEGIN
                    UPDATE products SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
            ''')
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_categories_timestamp 
                    AFTER UPDATE ON categories
                BEGIN
                    UPDATE categories SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
            ''')
            
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_payments_timestamp 
                    AFTER UPDATE ON payments
                BEGIN
                    UPDATE payments SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END;
            ''')
            
            # Insert default categories
            default_categories = [
                'Bakery', 'Beverages', 'Stationery', 'Electronics',
                'Health_Beauty', 'Household', 'Stationery', 'Toys', 'Grocery'
            ]
            
            for category in default_categories:
                cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
            
            # Insert sample products
            sample_products = [
                ('Lifebuoy(100g)', '54745', 10, 53.00, 50.00, 'Health_Beauty'),
                ('Signal(70g)', '98765', 15, 80.00, 100.00, 'Health_Beauty'),
                ('Anchor(400g)', '09654', 10, 120.00, 550.00, 'Household'),
                ('Vim(500ml)', '47484', 12, 215.00, 210.00, 'Household'),
                ('Viva(400g)', '93848', 18, 332.00, 330.00, 'Household'),
                ('Marmite(210g)', '36372', 5, 573.00, 570.00, 'Household'),
                ('Laojee(400)', '09837', 17, 376.00, 374.00, 'Beverages'),
                ('Samba rice', '12653', 22, 100.00, 97.00, 'Household'),
                ('Watawala Tea(100g)', '44560', 25, 122.00, 120.00, 'Beverages'),
                ('Maliban marie(330g)', '11232', 22, 147.00, 144.00, 'Bakery')
            ]
            
            for product in sample_products:
                name, sku, qty, sell_price, purchase_price, category = product
                cursor.execute('''
                    INSERT OR IGNORE INTO products 
                    (name, sku, qty, sell_price, purchase_price, category_id)
                    VALUES (?, ?, ?, ?, ?, (SELECT id FROM categories WHERE name = ?))
                ''', (name, sku, qty, sell_price, purchase_price, category))
            
            # Commit all changes
            conn.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            print(f"An error occurred during migration: {str(e)}")
            conn.rollback()
            raise
        
        finally:
            conn.close()
            
    def reset_database(self):
        """Drop all tables and recreate them"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Drop existing tables
            cursor.execute("DROP TABLE IF EXISTS payments")
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS categories")
            
            conn.commit()
            print("Database reset completed!")
            
            # Recreate tables
            self.create_database()
            
        except Exception as e:
            print(f"An error occurred during database reset: {str(e)}")
            conn.rollback()
            raise
        
        finally:
            conn.close()

if __name__ == "__main__":
    # Usage example
    migration = DatabaseMigration()
    
    # To create/update the database
    #migration.create_database()
    
    # To reset the database (uncomment if needed)
    migration.reset_database()