"""
Seed data generator for the Retail Sales Intelligence Platform.

Generates ~5000 realistic Superstore-style retail sales records and inserts
them into the database along with a test user account.

Usage: python seed_data.py
"""
import os
import sys
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from database import SessionLocal, Base, engine
from models.user import User
from models.dataset import Dataset, SalesRecord
from services.auth_service import hash_password

# Reproducibility
random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------------
# Data dictionaries
# ---------------------------------------------------------------------------

REGIONS = {
    'East': {
        'New York': ['New York City', 'Buffalo', 'Rochester', 'Albany'],
        'Pennsylvania': ['Philadelphia', 'Pittsburgh', 'Allentown'],
        'Massachusetts': ['Boston', 'Worcester', 'Springfield'],
        'Connecticut': ['Hartford', 'New Haven', 'Stamford'],
        'New Jersey': ['Newark', 'Jersey City', 'Trenton'],
        'Maryland': ['Baltimore', 'Annapolis', 'Rockville'],
        'Virginia': ['Virginia Beach', 'Richmond', 'Arlington']
    },
    'West': {
        'California': ['Los Angeles', 'San Francisco', 'San Diego', 'San Jose', 'Sacramento'],
        'Washington': ['Seattle', 'Spokane', 'Tacoma'],
        'Oregon': ['Portland', 'Salem', 'Eugene'],
        'Colorado': ['Denver', 'Colorado Springs', 'Aurora'],
        'Arizona': ['Phoenix', 'Tucson', 'Mesa'],
        'Nevada': ['Las Vegas', 'Reno', 'Henderson']
    },
    'Central': {
        'Illinois': ['Chicago', 'Springfield', 'Naperville'],
        'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
        'Ohio': ['Columbus', 'Cleveland', 'Cincinnati'],
        'Michigan': ['Detroit', 'Grand Rapids', 'Ann Arbor'],
        'Indiana': ['Indianapolis', 'Fort Wayne', 'Bloomington'],
        'Minnesota': ['Minneapolis', 'Saint Paul', 'Rochester'],
        'Wisconsin': ['Milwaukee', 'Madison', 'Green Bay']
    },
    'South': {
        'Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville'],
        'Georgia': ['Atlanta', 'Savannah', 'Augusta'],
        'North Carolina': ['Charlotte', 'Raleigh', 'Durham'],
        'Tennessee': ['Nashville', 'Memphis', 'Knoxville'],
        'Alabama': ['Birmingham', 'Montgomery', 'Huntsville'],
        'Louisiana': ['New Orleans', 'Baton Rouge', 'Shreveport']
    }
}

CATEGORIES = {
    'Furniture': {
        'Chairs': ['Executive Office Chair', 'Ergonomic Mesh Chair', 'Stacking Chair', 'Conference Chair', 'Folding Chair'],
        'Tables': ['Conference Table', 'Standing Desk', 'Round Table', 'Folding Table', 'Corner Desk'],
        'Bookcases': ['5-Shelf Bookcase', '3-Shelf Bookcase', 'Stackable Bookcase', 'Corner Bookcase'],
        'Furnishings': ['Desk Lamp', 'Wall Clock', 'Picture Frame', 'Coat Rack', 'Floor Mat']
    },
    'Office Supplies': {
        'Paper': ['Copy Paper', 'Legal Pads', 'Sticky Notes', 'Notebook', 'Card Stock'],
        'Binders': ['3-Ring Binder', 'Presentation Binder', 'Report Cover', 'Folder Set'],
        'Storage': ['File Cabinet', 'Storage Box', 'Desk Organizer', 'Magazine Rack'],
        'Art': ['Markers Set', 'Colored Pencils', 'Sketch Pad', 'Paint Set'],
        'Envelopes': ['Business Envelopes', 'Manila Envelopes', 'Padded Mailers'],
        'Labels': ['Address Labels', 'File Labels', 'Name Tags'],
        'Fasteners': ['Paper Clips', 'Stapler', 'Binder Clips', 'Rubber Bands'],
        'Supplies': ['Scissors', 'Tape Dispenser', 'Glue Sticks', 'Push Pins']
    },
    'Technology': {
        'Phones': ['Samsung Galaxy Phone', 'iPhone Pro', 'Google Pixel', 'Desk Phone', 'Wireless Headset'],
        'Accessories': ['USB Hub', 'Wireless Mouse', 'Keyboard', 'Monitor Stand', 'Webcam', 'Cable Kit'],
        'Machines': ['HP LaserJet Printer', 'Brother Inkjet Printer', 'Desktop Computer', 'All-in-One Printer'],
        'Copiers': ['Canon Copier', 'Xerox Machine', 'Ricoh Copier', 'Sharp Copier']
    }
}

# Sales ranges by category (min, max)
SALES_RANGES = {
    'Technology': (50, 2000),
    'Furniture': (30, 1500),
    'Office Supplies': (5, 500)
}

# Customer name pools
FIRST_NAMES = [
    'James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda',
    'David', 'Elizabeth', 'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Christopher', 'Karen', 'Charles', 'Lisa', 'Daniel', 'Nancy',
    'Matthew', 'Betty', 'Anthony', 'Margaret', 'Mark', 'Sandra', 'Donald', 'Ashley',
    'Steven', 'Dorothy', 'Paul', 'Kimberly', 'Andrew', 'Emily', 'Joshua', 'Donna'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores'
]

# Build ~200 unique customer names
customers = []
for i in range(200):
    first = FIRST_NAMES[i % len(FIRST_NAMES)]
    last = LAST_NAMES[i % len(LAST_NAMES)]
    customers.append(f'{first} {last}')

customers = list(set(customers))
if len(customers) < 200:
    for i in range(200 - len(customers)):
        customers.append(
            f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {chr(65 + i % 26)}'
        )
customers = customers[:200]

# Segment distribution: Consumer 52%, Corporate 30%, Home Office 18%
SEGMENTS = ['Consumer'] * 52 + ['Corporate'] * 30 + ['Home Office'] * 18

# Ship mode distribution
SHIP_MODES = ['Standard Class'] * 60 + ['Second Class'] * 20 + ['First Class'] * 15 + ['Same Day'] * 5

# Processing days by ship mode (min, max)
PROCESSING_DAYS = {
    'Standard Class': (5, 7),
    'Second Class': (3, 5),
    'First Class': (2, 3),
    'Same Day': (0, 1)
}

# Discount distribution (many orders have no discount)
DISCOUNTS = [0, 0, 0, 0, 0.1, 0.1, 0.15, 0.2, 0.3]


def generate_records(n=5000):
    """Generate n realistic retail sales records as a DataFrame."""
    records = []
    order_counter = 1

    for i in range(n):
        # Date: Jan 2022 to Dec 2023
        year = random.choice([2022, 2023])
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Safe for all months
        order_date = datetime(year, month, day)

        # Seasonal sales multiplier: Q4 boost, Q1 dip
        seasonal_multiplier = 1.0
        if month in [10, 11, 12]:
            seasonal_multiplier = 1.3
        elif month in [1, 2, 3]:
            seasonal_multiplier = 0.8

        # Ship mode and processing time
        ship_mode = random.choice(SHIP_MODES)
        proc_days = random.randint(*PROCESSING_DAYS[ship_mode])
        ship_date = order_date + timedelta(days=proc_days)

        # Location
        region = random.choice(list(REGIONS.keys()))
        state = random.choice(list(REGIONS[region].keys()))
        city = random.choice(REGIONS[region][state])

        # Product
        category = random.choice(list(CATEGORIES.keys()))
        sub_category = random.choice(list(CATEGORIES[category].keys()))
        product_name = random.choice(CATEGORIES[category][sub_category])

        # Customer
        customer_name = random.choice(customers)
        customer_id = f'CUS-{hash(customer_name) % 10000:04d}'
        segment = random.choice(SEGMENTS)

        # Financial values - log-normal gives realistic "many small, few large" distribution
        sales_min, sales_max = SALES_RANGES[category]
        sales = np.random.lognormal(mean=np.log((sales_min + sales_max) / 4), sigma=0.8)
        sales = np.clip(sales, sales_min, sales_max) * seasonal_multiplier
        sales = round(float(sales), 2)

        quantity = random.choices(
            range(1, 15),
            weights=[30, 20, 15, 10, 8, 5, 4, 3, 2, 1, 1, 1, 0, 0],
            k=1
        )[0]
        discount = random.choice(DISCOUNTS)

        # Profit: base margin minus discount impact plus random noise
        base_margin = random.uniform(0.05, 0.35)
        profit = sales * base_margin - sales * discount * 0.5 + random.uniform(-20, 20)
        profit = round(float(profit), 2)

        order_id = f'ORD-{year}-{order_counter:05d}'
        order_counter += 1

        records.append({
            'Order ID': order_id,
            'Order Date': order_date.strftime('%Y-%m-%d'),
            'Ship Date': ship_date.strftime('%Y-%m-%d'),
            'Ship Mode': ship_mode,
            'Customer ID': customer_id,
            'Customer Name': customer_name,
            'Segment': segment,
            'City': city,
            'State': state,
            'Region': region,
            'Category': category,
            'Sub-Category': sub_category,
            'Product Name': product_name,
            'Sales': sales,
            'Quantity': quantity,
            'Discount': discount,
            'Profit': profit
        })

    return pd.DataFrame(records)


def main():
    print('=== Retail Intelligence Platform - Seed Data Generator ===')
    print()

    # Create tables
    Base.metadata.create_all(bind=engine)
    print('Database tables created.')

    db = SessionLocal()

    try:
        # Check if seed data already exists
        existing = db.query(User).filter(User.email == 'test@example.com').first()
        if existing:
            print('Seed data already exists. Skipping...')
            print('To re-seed, delete the test user and associated data first.')
            return

        # 1. Create test user
        test_user = User(
            email='test@example.com',
            name='Test User',
            hashed_password=hash_password('password123')
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f'Created test user: test@example.com / password123')

        # 2. Generate data
        print('Generating 5000 sales records...')
        df = generate_records(5000)

        # 3. Save CSV
        os.makedirs('uploads', exist_ok=True)
        csv_path = os.path.join('uploads', 'seed_data.csv')
        df.to_csv(csv_path, index=False)
        print(f'Saved CSV to {csv_path}')

        # 4. Create dataset entry
        dataset = Dataset(
            user_id=test_user.id,
            filename='seed_data.csv',
            row_count=len(df),
            column_count=len(df.columns),
            status='processed',
            upload_stats=json.dumps({
                'original_rows': len(df),
                'duplicates_removed': 0,
                'missing_values_filled': 0,
                'invalid_rows_removed': 0,
                'final_rows': len(df)
            })
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        print(f'Created dataset entry (ID: {dataset.id})')

        # 5. Insert sales records
        print('Inserting records into database...')
        records = []
        for _, row in df.iterrows():
            order_date = pd.to_datetime(row['Order Date'])
            ship_date = pd.to_datetime(row['Ship Date'])

            sales_val = float(row['Sales'])
            profit_val = float(row['Profit'])
            margin = round(profit_val / sales_val * 100, 2) if sales_val > 0 else 0.0
            proc_days = (ship_date - order_date).days

            record = SalesRecord(
                dataset_id=dataset.id,
                order_id=row['Order ID'],
                order_date=order_date.date(),
                ship_date=ship_date.date(),
                ship_mode=row['Ship Mode'],
                customer_id=row['Customer ID'],
                customer_name=row['Customer Name'],
                segment=row['Segment'],
                city=row['City'],
                state=row['State'],
                region=row['Region'],
                category=row['Category'],
                sub_category=row['Sub-Category'],
                product_name=row['Product Name'],
                sales=sales_val,
                quantity=int(row['Quantity']),
                discount=float(row['Discount']),
                profit=profit_val,
                order_month=order_date.month,
                order_year=order_date.year,
                order_day_of_week=order_date.dayofweek,
                profit_margin=margin,
                processing_days=proc_days
            )
            records.append(record)

        db.bulk_save_objects(records)
        db.commit()
        print(f'Inserted {len(records)} sales records.')

        # 6. Print summary
        print()
        print('=== Summary ===')
        print(f'Total Records: {len(df)}')
        print(f'Date Range: {df["Order Date"].min()} to {df["Order Date"].max()}')
        print(f'Regions: {df["Region"].nunique()}')
        print(f'Categories: {df["Category"].nunique()}')
        print(f'Unique Customers: {df["Customer Name"].nunique()}')
        print(f'Total Revenue: ${df["Sales"].sum():,.2f}')
        print(f'Total Profit: ${df["Profit"].sum():,.2f}')
        print(f'Avg Order Value: ${df["Sales"].mean():,.2f}')
        print()
        print('Revenue by Category:')
        for cat, rev in df.groupby('Category')['Sales'].sum().items():
            print(f'  {cat}: ${rev:,.2f}')
        print()
        print('Revenue by Region:')
        for reg, rev in df.groupby('Region')['Sales'].sum().items():
            print(f'  {reg}: ${rev:,.2f}')
        print()
        print('Seed data generation complete!')

    finally:
        db.close()


if __name__ == '__main__':
    main()
