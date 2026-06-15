import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Show all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

# Show all products
cursor.execute("SELECT * FROM products")
products = cursor.fetchall()
print("\nProducts:")
for product in products:
    print(product)

conn.close()