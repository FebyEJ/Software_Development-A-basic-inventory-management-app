from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Serve the HTML page
@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f: # Added encoding='utf-8'
        return f.read()

# Initialize database
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0
        )
    ''')
    
    # Only add sample data if table is empty
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Battery AA', 12, 1.5),
            ('HDMI Cable', 3, 8.99),
            ('USB Charger', 8, 12.99),
            ('Phone Case', 15, 15.99),
            ('Screen Protector', 7, 4.99),
        ]
        cursor.executemany(
            "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
            sample_products
        )
        print("✅ Added sample products")
    
    conn.commit()
    conn.close()
    print("✅ Database ready")

# API: Get all products
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, price FROM products ORDER BY name")
    products = cursor.fetchall()
    conn.close()
    
    return jsonify([{'id': p[0], 'name': p[1], 'quantity': p[2], 'price': p[3]} for p in products])

# API: Add new product
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    name = data.get('name')
    quantity = data.get('quantity', 0)
    price = data.get('price', 0.0)
    
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
        (name, quantity, price)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': product_id, 'message': 'Product added'}), 201

# API: Delete product
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT id FROM products WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product deleted'})

# API: Update stock quantity
@app.route('/api/products/<int:id>/stock', methods=['PATCH'])
def update_stock(id):
    data = request.json
    new_quantity = data.get('quantity')
    
    if new_quantity is None:
        return jsonify({'error': 'Quantity is required'}), 400
    
    if new_quantity < 0:
        return jsonify({'error': 'Quantity cannot be negative'}), 400
    
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT id FROM products WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    # Update the quantity
    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Stock updated successfully'})

# API: Update product (edit name or price)
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.json
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute("SELECT id FROM products WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    # Update fields
    if 'name' in data:
        cursor.execute("UPDATE products SET name = ? WHERE id = ?", (data['name'], id))
    if 'price' in data:
        cursor.execute("UPDATE products SET price = ? WHERE id = ?", (data['price'], id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product updated successfully'})

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 Server running at: http://localhost:3000")
    print("📝 You can now:")
    print("   - View products")
    print("   - Add new products")
    print("   - Delete products")
    print("="*50 + "\n")
    app.run(port=3000, debug=True)