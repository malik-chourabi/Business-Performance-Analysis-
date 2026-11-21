"""Builds sql/superstore.db from data/processed/cleaned_sales.csv (run from project root: python sql/create_database.py)."""
import sqlite3, pandas as pd, os
db = 'sql/superstore.db'
if os.path.exists(db): os.remove(db)
df = pd.read_csv('data/processed/cleaned_sales.csv', dtype={'Postal Code': str})
for c in ['Order Date', 'Ship Date']: df[c] = pd.to_datetime(df[c]).dt.strftime('%Y-%m-%d')
con = sqlite3.connect(db); cur = con.cursor(); cur.execute('PRAGMA foreign_keys = ON')
cur.executescript("""
CREATE TABLE sales_clean (            -- flat table: exactly the cleaned CSV (one row per order line)
  row_id INTEGER PRIMARY KEY, order_id TEXT, order_date TEXT, ship_date TEXT, ship_mode TEXT,
  customer_id TEXT, customer_name TEXT, segment TEXT, country TEXT, city TEXT, state TEXT, postal_code TEXT, region TEXT,
  product_id TEXT, category TEXT, sub_category TEXT, product_name TEXT,
  sales REAL, quantity INTEGER, discount REAL, profit REAL,
  product_name_original TEXT, possible_duplicate INTEGER, order_year INTEGER, order_quarter INTEGER, order_month INTEGER,
  order_month_name TEXT, year_month TEXT, shipping_days INTEGER, profit_margin REAL, cost REAL, is_loss INTEGER, discount_band TEXT, discount_group TEXT);
CREATE TABLE dim_customer (customer_id TEXT PRIMARY KEY, customer_name TEXT NOT NULL, segment TEXT NOT NULL);
CREATE TABLE dim_product  (product_id TEXT PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL, sub_category TEXT NOT NULL);
CREATE TABLE dim_geography(geo_id INTEGER PRIMARY KEY, country TEXT, region TEXT, state TEXT, city TEXT, postal_code TEXT,
                           UNIQUE(country, region, state, city, postal_code));
CREATE TABLE orders (order_id TEXT PRIMARY KEY, order_date TEXT NOT NULL, ship_date TEXT NOT NULL, ship_mode TEXT NOT NULL,
                     customer_id TEXT NOT NULL REFERENCES dim_customer(customer_id), geo_id INTEGER NOT NULL REFERENCES dim_geography(geo_id));
CREATE TABLE order_lines (row_id INTEGER PRIMARY KEY, order_id TEXT NOT NULL REFERENCES orders(order_id),
                          product_id TEXT NOT NULL REFERENCES dim_product(product_id),
                          sales REAL NOT NULL, quantity INTEGER NOT NULL, discount REAL NOT NULL, profit REAL NOT NULL);
""")
d = df.rename(columns={c: c.lower().replace('-', '_').replace(' ', '_') for c in df.columns})
d.to_sql('sales_clean', con, if_exists='append', index=False)
cur.execute("INSERT INTO dim_customer SELECT DISTINCT customer_id, customer_name, segment FROM sales_clean")
cur.execute("INSERT INTO dim_product SELECT product_id, MIN(product_name), MIN(category), MIN(sub_category) FROM sales_clean GROUP BY product_id")
cur.execute("INSERT INTO dim_geography(country, region, state, city, postal_code) SELECT DISTINCT country, region, state, city, postal_code FROM sales_clean ORDER BY region, state, city, postal_code")
cur.execute("""INSERT INTO orders SELECT s.order_id, MIN(s.order_date), MIN(s.ship_date), MIN(s.ship_mode), MIN(s.customer_id), MIN(g.geo_id)
               FROM sales_clean s JOIN dim_geography g ON g.country=s.country AND g.region=s.region AND g.state=s.state AND g.city=s.city AND g.postal_code=s.postal_code
               GROUP BY s.order_id""")
cur.execute("INSERT INTO order_lines SELECT row_id, order_id, product_id, sales, quantity, discount, profit FROM sales_clean")
cur.executescript("CREATE INDEX ix_lines_order ON order_lines(order_id); CREATE INDEX ix_lines_prod ON order_lines(product_id); CREATE INDEX ix_orders_cust ON orders(customer_id); CREATE INDEX ix_orders_date ON orders(order_date);")
con.commit()
for t in ['sales_clean','dim_customer','dim_product','dim_geography','orders','order_lines']:
    print(t, cur.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0])
print('FK violations:', cur.execute('PRAGMA foreign_key_check').fetchall())
print('Orders with >1 geography/ship mode in source:', cur.execute("SELECT COUNT(*) FROM (SELECT order_id FROM sales_clean GROUP BY order_id HAVING COUNT(DISTINCT city||state||postal_code)>1 OR COUNT(DISTINCT ship_mode)>1 OR COUNT(DISTINCT order_date)>1)").fetchone()[0])
con.close()
