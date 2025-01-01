import sqlite3

def seed_categories():
    conn = sqlite3.connect('Data/database.db')
    cursor = conn.cursor()
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Add category column to products table
    cursor.execute('PRAGMA table_info(products)')
    columns = cursor.fetchall()
    if not any(column[1] == 'category_id' for column in columns):
        cursor.execute('ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)')
    
    # Seed initial categories
    categories = [
        ('Beverages',),
        ('Stationery',),
        ('Bakery',),
        ('Household',),
        ('Books',),
        ('Toys',),
        ('Electronics',),
        ('Health & Beauty',)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO categories (name) VALUES (?)', categories)
    conn.commit()
    conn.close()

# Run seeder
if __name__ == "__main__":
    seed_categories()