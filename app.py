from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database configuration
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

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

# Product routes
@app.route('/products')
def view_products():
    """View all products"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    """Add new product"""
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        description = request.form['description']
        
        if not product_id or not product_name:
            flash('Product ID and Name are required!', 'error')
            return render_template('add_product.html')
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Product (product_id, product_name, description) VALUES (?, ?, ?)',
                        (product_id, product_name, description))
            conn.commit()
            conn.close()
            flash('Product added successfully!', 'success')
            return redirect(url_for('view_products'))
        except sqlite3.IntegrityError:
            flash('Product ID already exists!', 'error')
            return render_template('add_product.html')
    
    return render_template('add_product.html')

@app.route('/products/edit/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    """Edit product"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        
        if not product_name:
            flash('Product Name is required!', 'error')
            product = conn.execute('SELECT * FROM Product WHERE product_id = ?', (product_id,)).fetchone()
            conn.close()
            return render_template('edit_product.html', product=product)
        
        conn.execute('UPDATE Product SET product_name = ?, description = ? WHERE product_id = ?',
                    (product_name, description, product_id))
        conn.commit()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('view_products'))
    
    product = conn.execute('SELECT * FROM Product WHERE product_id = ?', (product_id,)).fetchone()
    conn.close()
    
    if product is None:
        flash('Product not found!', 'error')
        return redirect(url_for('view_products'))
    
    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<product_id>')
def delete_product(product_id):
    """Delete product"""
    conn = get_db_connection()
    
    # Check if product has movements
    movements = conn.execute('SELECT COUNT(*) as count FROM ProductMovement WHERE product_id = ?', (product_id,)).fetchone()
    
    if movements['count'] > 0:
        flash('Cannot delete product with existing movements!', 'error')
        conn.close()
        return redirect(url_for('view_products'))
    
    conn.execute('DELETE FROM Product WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('view_products'))

# Location routes
@app.route('/locations')
def view_locations():
    """View all locations"""
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET', 'POST'])
def add_location():
    """Add new location"""
    if request.method == 'POST':
        location_id = request.form['location_id']
        location_name = request.form['location_name']
        address = request.form['address']
        
        if not location_id or not location_name:
            flash('Location ID and Name are required!', 'error')
            return render_template('add_location.html')
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO Location (location_id, location_name, address) VALUES (?, ?, ?)',
                        (location_id, location_name, address))
            conn.commit()
            conn.close()
            flash('Location added successfully!', 'success')
            return redirect(url_for('view_locations'))
        except sqlite3.IntegrityError:
            flash('Location ID already exists!', 'error')
            return render_template('add_location.html')
    
    return render_template('add_location.html')

@app.route('/locations/edit/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    """Edit location"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        address = request.form['address']
        
        if not location_name:
            flash('Location Name is required!', 'error')
            location = conn.execute('SELECT * FROM Location WHERE location_id = ?', (location_id,)).fetchone()
            conn.close()
            return render_template('edit_location.html', location=location)
        
        conn.execute('UPDATE Location SET location_name = ?, address = ? WHERE location_id = ?',
                    (location_name, address, location_id))
        conn.commit()
        conn.close()
        flash('Location updated successfully!', 'success')
        return redirect(url_for('view_locations'))
    
    location = conn.execute('SELECT * FROM Location WHERE location_id = ?', (location_id,)).fetchone()
    conn.close()
    
    if location is None:
        flash('Location not found!', 'error')
        return redirect(url_for('view_locations'))
    
    return render_template('edit_location.html', location=location)

@app.route('/locations/delete/<location_id>')
def delete_location(location_id):
    """Delete location"""
    conn = get_db_connection()
    
    # Check if location has movements
    movements = conn.execute('SELECT COUNT(*) as count FROM ProductMovement WHERE from_location = ? OR to_location = ?', 
                           (location_id, location_id)).fetchone()
    
    if movements['count'] > 0:
        flash('Cannot delete location with existing movements!', 'error')
        conn.close()
        return redirect(url_for('view_locations'))
    
    conn.execute('DELETE FROM Location WHERE location_id = ?', (location_id,))
    conn.commit()
    conn.close()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('view_locations'))

# Movement routes
@app.route('/movements')
def view_movements():
    """View all movements"""
    conn = get_db_connection()
    movements = conn.execute('''
        SELECT pm.*, p.product_name, 
               fl.location_name as from_location_name,
               tl.location_name as to_location_name
        FROM ProductMovement pm
        JOIN Product p ON pm.product_id = p.product_id
        LEFT JOIN Location fl ON pm.from_location = fl.location_id
        LEFT JOIN Location tl ON pm.to_location = tl.location_id
        ORDER BY pm.timestamp DESC
    ''').fetchall()
    conn.close()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET', 'POST'])
def add_movement():
    """Add new movement"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location'] if request.form['from_location'] else None
        to_location = request.form['to_location'] if request.form['to_location'] else None
        qty = int(request.form['qty'])
        
        if not product_id or not qty:
            flash('Product and Quantity are required!', 'error')
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('add_movement.html', products=products, locations=locations)
        
        if not from_location and not to_location:
            flash('Either From Location or To Location must be specified!', 'error')
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('add_movement.html', products=products, locations=locations)
        
        movement_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            conn.execute('''
                INSERT INTO ProductMovement (movement_id, timestamp, from_location, to_location, product_id, qty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (movement_id, timestamp, from_location, to_location, product_id, qty))
            conn.commit()
            conn.close()
            flash('Movement added successfully!', 'success')
            return redirect(url_for('view_movements'))
        except sqlite3.IntegrityError as e:
            flash(f'Error adding movement: {str(e)}', 'error')
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('add_movement.html', products=products, locations=locations)
    
    products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
    conn.close()
    return render_template('add_movement.html', products=products, locations=locations)

@app.route('/movements/edit/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    """Edit movement"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location'] if request.form['from_location'] else None
        to_location = request.form['to_location'] if request.form['to_location'] else None
        qty = int(request.form['qty'])
        
        if not product_id or not qty:
            flash('Product and Quantity are required!', 'error')
            movement = conn.execute('SELECT * FROM ProductMovement WHERE movement_id = ?', (movement_id,)).fetchone()
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
        
        if not from_location and not to_location:
            flash('Either From Location or To Location must be specified!', 'error')
            movement = conn.execute('SELECT * FROM ProductMovement WHERE movement_id = ?', (movement_id,)).fetchone()
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
        
        try:
            conn.execute('''
                UPDATE ProductMovement 
                SET product_id = ?, from_location = ?, to_location = ?, qty = ?
                WHERE movement_id = ?
            ''', (product_id, from_location, to_location, qty, movement_id))
            conn.commit()
            conn.close()
            flash('Movement updated successfully!', 'success')
            return redirect(url_for('view_movements'))
        except sqlite3.IntegrityError as e:
            flash(f'Error updating movement: {str(e)}', 'error')
            movement = conn.execute('SELECT * FROM ProductMovement WHERE movement_id = ?', (movement_id,)).fetchone()
            products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
            locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
            conn.close()
            return render_template('edit_movement.html', movement=movement, products=products, locations=locations)
    
    movement = conn.execute('SELECT * FROM ProductMovement WHERE movement_id = ?', (movement_id,)).fetchone()
    products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
    conn.close()
    
    if movement is None:
        flash('Movement not found!', 'error')
        return redirect(url_for('view_movements'))
    
    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)

@app.route('/movements/delete/<movement_id>')
def delete_movement(movement_id):
    """Delete movement"""
    conn = get_db_connection()
    conn.execute('DELETE FROM ProductMovement WHERE movement_id = ?', (movement_id,))
    conn.commit()
    conn.close()
    flash('Movement deleted successfully!', 'success')
    return redirect(url_for('view_movements'))

# Balance report
@app.route('/balance-report')
def balance_report():
    """Generate balance report"""
    conn = get_db_connection()
    
    # Get all products and locations
    products = conn.execute('SELECT * FROM Product ORDER BY product_name').fetchall()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_name').fetchall()
    
    # Calculate balances
    balances = []
    for product in products:
        for location in locations:
            # Calculate incoming quantity (to_location)
            incoming = conn.execute('''
                SELECT COALESCE(SUM(qty), 0) as total
                FROM ProductMovement 
                WHERE product_id = ? AND to_location = ?
            ''', (product['product_id'], location['location_id'])).fetchone()
            
            # Calculate outgoing quantity (from_location)
            outgoing = conn.execute('''
                SELECT COALESCE(SUM(qty), 0) as total
                FROM ProductMovement 
                WHERE product_id = ? AND from_location = ?
            ''', (product['product_id'], location['location_id'])).fetchone()
            
            balance = incoming['total'] - outgoing['total']
            
            if balance != 0:  # Only show non-zero balances
                balances.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'location_id': location['location_id'],
                    'location_name': location['location_name'],
                    'balance': balance
                })
    
    conn.close()
    return render_template('balance_report.html', balances=balances)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
