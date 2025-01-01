import sqlite3

def create_payments_table():    
    try:
        conn = sqlite3.connect('Data/database.db')
        cursor = conn.cursor()
        
        # Create payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Commit the changes
        conn.commit()
        print("Payments table created successfully!")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    create_payments_table()