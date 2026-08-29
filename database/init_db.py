"""
Initialize the QueryOpt AI demo SQLite database.
Generates schema and synthetic seed data (~500 customers, 200 products, 2000 orders, 5000 items, 300 employees).
"""
import os
import sqlite3
import random
from datetime import datetime, timedelta

def init_database(db_path: str = None):
    if db_path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "demo.db")

    print(f"Initializing demo database at: {db_path}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    # Remove existing db if present to ensure clean state
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception as e:
            print(f"Warning removing old DB: {e}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    print("[OK] Schema created successfully")

    # Seed data generator
    random.seed(42)  # Deterministic seed data

    # 1. Departments
    departments = [
        ("Engineering", 1500000.0, "Building A, Floor 3"),
        ("Product Management", 800000.0, "Building A, Floor 4"),
        ("Design", 400000.0, "Building A, Floor 2"),
        ("Sales", 1200000.0, "Building B, Floor 1"),
        ("Marketing", 900000.0, "Building B, Floor 2"),
        ("Human Resources", 350000.0, "Building C, Floor 1"),
        ("Finance & Accounting", 600000.0, "Building C, Floor 2"),
        ("Customer Support", 500000.0, "Building B, Floor 3"),
        ("Legal & Compliance", 450000.0, "Building C, Floor 3"),
        ("Operations & Logistics", 1100000.0, "Warehouse 1"),
    ]
    cursor.executemany(
        "INSERT INTO departments (name, budget, location) VALUES (?, ?, ?)",
        departments
    )

    # 2. Suppliers
    countries = ["USA", "Germany", "Japan", "South Korea", "China", "UK", "Canada", "Taiwan", "France", "India"]
    supplier_names = [
        "TechCore Supplies", "Global Semiconductor Co", "Apex Circuit Systems", "Quantum Components",
        "Pacific Display Ltd", "Nordic Raw Materials", "Alpine Precision Gears", "Sakura Audio Labs",
        "EuroFast Logistics Packaging", "Sinotech Assemblies", "Vanguard Fiber Optics", "OmniTech Hardware",
        "Pioneer Battery Tech", "Silverline Connectors", "Atlas Heavy Plastics", "Starlight Sensor Systems",
        "Nexus Microelectronics", "Horizon Rubber & Seals", "Zenith Power Units", "Prime Mold Solutions"
    ]
    suppliers = []
    for name in supplier_names:
        c = random.choice(countries)
        email = f"contact@{name.lower().replace(' ', '')}.com"
        suppliers.append((name, c, email))
    cursor.executemany(
        "INSERT INTO suppliers (name, country, contact_email) VALUES (?, ?, ?)",
        suppliers
    )

    # 3. Products
    categories = ["Electronics", "Clothing", "Books", "Food & Beverages", "Sports & Outdoors", "Home & Kitchen", "Automotive"]
    product_prefixes = ["Pro", "Ultra", "Max", "Eco", "Smart", "Super", "Elite", "Prime", "Compact", "Hyper"]
    product_nouns = [
        "Laptop", "Smartphone", "Monitor", "Keyboard", "Headphones", "Camera", "Smartwatch", "Drone",
        "Jacket", "Sneakers", "T-Shirt", "Jeans", "Backpack", "Cap", "Hoodie", "Gloves",
        "Novel", "Cookbook", "Science Journal", "Atlas", "Encyclopedia", "Biography", "Dictionary",
        "Coffee Beans", "Green Tea", "Dark Chocolate", "Energy Bar", "Olive Oil", "Spices Set",
        "Bicycle", "Yoga Mat", "Dumbbells", "Running Shoes", "Tent", "Sleeping Bag", "Water Bottle"
    ]
    products = []
    for i in range(1, 201):
        name = f"{random.choice(product_prefixes)} {random.choice(product_nouns)} v{random.randint(1, 9)}"
        cat = random.choice(categories)
        price = round(random.uniform(9.99, 1499.99), 2)
        stock = random.randint(5, 500)
        sup_id = random.randint(1, len(suppliers))
        products.append((name, cat, price, stock, sup_id))
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock_quantity, supplier_id) VALUES (?, ?, ?, ?, ?)",
        products
    )

    # 4. Customers
    first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth",
                   "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen",
                   "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                  "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                  "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
              "Dallas", "San Jose", "Austin", "Jacksonville", "San Francisco", "Columbus", "Fort Worth", "Indianapolis",
              "Charlotte", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Portland"]
    
    customers = []
    base_date = datetime(2021, 1, 1)
    for i in range(1, 501):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        city = random.choice(cities)
        country = "USA"
        created = (base_date + timedelta(days=random.randint(0, 1400))).strftime("%Y-%m-%d %H:%M:%S")
        customers.append((fn, ln, email, city, country, created))
    cursor.executemany(
        "INSERT INTO customers (first_name, last_name, email, city, country, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        customers
    )

    # 5. Employees
    employees = []
    emp_base_date = datetime(2018, 1, 1)
    for i in range(1, 301):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        dept_id = random.randint(1, len(departments))
        manager_id = random.randint(1, max(1, i - 1)) if i > 10 and random.random() > 0.3 else None
        salary = round(random.uniform(45000, 180000), 2)
        jdate = (emp_base_date + timedelta(days=random.randint(0, 2400))).strftime("%Y-%m-%d")
        email = f"{fn.lower()}.{ln.lower()}.emp{i}@company.internal"
        employees.append((fn, ln, dept_id, manager_id, salary, jdate, email))
    cursor.executemany(
        "INSERT INTO employees (first_name, last_name, department_id, manager_id, salary, join_date, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
        employees
    )

    # 6. Orders & Order Items
    statuses = ["pending", "shipped", "delivered", "delivered", "delivered", "cancelled"]
    orders = []
    order_items = []
    order_base_date = datetime(2022, 1, 1)

    for order_id in range(1, 2001):
        cust_id = random.randint(1, 500)
        odate = (order_base_date + timedelta(days=random.randint(0, 1100))).strftime("%Y-%m-%d")
        status = random.choice(statuses)
        ship_city = random.choice(cities)
        
        # generate 1 to 5 items for this order
        num_items = random.randint(1, 5)
        order_total = 0.0
        for _ in range(num_items):
            prod_id = random.randint(1, 200)
            qty = random.randint(1, 4)
            # Find price roughly
            unit_price = round(random.uniform(10.0, 500.0), 2)
            item_total = qty * unit_price
            order_total += item_total
            order_items.append((order_id, prod_id, qty, unit_price))
        
        orders.append((cust_id, odate, status, round(order_total, 2), ship_city))

    cursor.executemany(
        "INSERT INTO orders (customer_id, order_date, status, total_amount, shipping_city) VALUES (?, ?, ?, ?, ?)",
        orders
    )

    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        order_items
    )

    conn.commit()

    # Print summary
    tables = ["departments", "suppliers", "customers", "products", "employees", "orders", "order_items"]
    print("[OK] Seed data loaded:")
    for t in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        cnt = cursor.fetchone()[0]
        print(f"  - {t:<14}: {cnt} rows")

    conn.close()
    print("Database initialized successfully!\n")

if __name__ == "__main__":
    init_database()
