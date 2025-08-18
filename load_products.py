import pandas as pd
from sqlalchemy import create_engine

# 1. Load CSV
csv_file = 'product_sales_simulated.csv'  # adjust path if needed
df = pd.read_csv(csv_file)

# 2. Clean 'price' column: remove all non-digit/non-dot chars
df['price'] = df['price'].astype(str).str.replace(r'[^\d\.]', '', regex=True)
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# 3. Clean 'week' and 'month' columns: convert to numeric, coerce errors to NaN, fill NaN with 0, convert to int
df['week'] = pd.to_numeric(df['week'], errors='coerce').fillna(0).astype(int)
df['month'] = pd.to_numeric(df['month'], errors='coerce').fillna(0).astype(int)

# 4. Clean 'sales' column if needed (to int)
df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0).astype(int)

# 5. Optional: if 'is_festival' is string, convert to boolean
if df['is_festival'].dtype == object:
    df['is_festival'] = df['is_festival'].map({'True': True, 'true': True, 'False': False, 'false': False}).fillna(False)

# 6. PostgreSQL connection info
user = 'postgres'
password = 'mypassword'  # replace with your password
host = 'host.docker.internal'  # or 'localhost' depending on your setup
port = '5433'  # your Postgres port
database = 'sales_db'

# 7. Create SQLAlchemy engine
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

# 8. Import cleaned DataFrame into PostgreSQL (replace table)
df.to_sql('product_sales_simulated', engine, if_exists='replace', index=False)

print("✅ CSV cleaned and imported successfully into PostgreSQL!")



