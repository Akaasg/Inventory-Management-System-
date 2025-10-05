#!/usr/bin/env python3
"""
Script to add test data to the inventory management system
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
import random

DATABASE = 'inventory.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Product table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            product_id TEXT PRIMARY KEY,
            product_name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Create Location table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Location (
            location_id TEXT PRIMARY KEY,
            location_name TEXT NOT NULL,
            address TEXT
        )
    ''')
    
    # Create ProductMovement table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ProductMovement (
            movement_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            from_location TEXT,
            to_location TEXT,
            product_id TEXT NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY (from_location) REFERENCES Location (location_id),
            FOREIGN KEY (to_location) REFERENCES Location (location_id),
            FOREIGN KEY (product_id) REFERENCES Product (product_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def clear_existing_data():
    """Clear existing data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM ProductMovement')
    cursor.execute('DELETE FROM Product')
    cursor.execute('DELETE FROM Location')
    
    conn.commit()
    conn.close()

def add_test_products():
    """Add test products"""
    products = [
        ('P001', 'Laptop Computer', 'High-performance laptop for business use'),
        ('P002', 'Office Chair', 'Ergonomic office chair with lumbar support'),
        ('P003', 'Wireless Mouse', 'Bluetooth wireless mouse with precision tracking'),
        ('P004', 'Monitor 24"', '24-inch LED monitor with Full HD resolution')
    ]
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for product_id, product_name, description in products:
        cursor.execute('INSERT INTO Product (product_id, product_name, description) VALUES (?, ?, ?)',
                      (product_id, product_name, description))
    
    conn.commit()
    conn.close()
    print(f"Added {len(products)} products")

def add_test_locations():
    """Add test locations"""
    locations = [
        ('L001', 'Main Warehouse', '123 Industrial Ave, City Center'),
        ('L002', 'Office Building A', '456 Business St, Downtown'),
        ('L003', 'Retail Store', '789 Shopping Mall, West Side'),
        ('L004', 'Distribution Center', '321 Logistics Blvd, East End')
    ]
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for location_id, location_name, address in locations:
        cursor.execute('INSERT INTO Location (location_id, location_name, address) VALUES (?, ?, ?)',
                      (location_id, location_name, address))
    
    conn.commit()
    conn.close()
    print(f"Added {len(locations)} locations")

def add_test_movements():
    """Add test movements"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get products and locations
    products = cursor.execute('SELECT product_id FROM Product').fetchall()
    locations = cursor.execute('SELECT location_id FROM Location').fetchall()
    
    product_ids = [p[0] for p in products]
    location_ids = [l[0] for l in locations]
    
    movements = []
    
    # Generate 20 random movements
    for i in range(20):
        movement_id = str(uuid.uuid4())
        
        # Random timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        product_id = random.choice(product_ids)
        qty = random.randint(1, 50)
        
        # Random movement type
        movement_type = random.choice(['incoming', 'outgoing', 'transfer'])
        
        if movement_type == 'incoming':
            from_location = None
            to_location = random.choice(location_ids)
        elif movement_type == 'outgoing':
            from_location = random.choice(location_ids)
            to_location = None
        else:  # transfer
            from_location = random.choice(location_ids)
            to_location = random.choice([loc for loc in location_ids if loc != from_location])
        
        movements.append((movement_id, timestamp_str, from_location, to_location, product_id, qty))
    
    # Insert movements
    cursor.executemany('''
        INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', movements)
    
    conn.commit()
    conn.close()
    print(f"Added {len(movements)} movements")

def main():
    """Main function to add all test data"""
    print("Initializing database...")
    init_db()
    
    print("Clearing existing data...")
    clear_existing_data()
    
    print("Adding test products...")
    add_test_products()
    
    print("Adding test locations...")
    add_test_locations()
    
    print("Adding test movements...")
    add_test_movements()
    
    print("\nTest data added successfully!")
    print("You can now run the Flask application with: python app.py")

if __name__ == '__main__':
    main()


