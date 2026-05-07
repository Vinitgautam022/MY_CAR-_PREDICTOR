import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# 🔧 Config
data_path = "path/to/data_lake"
db_conn_str = "postgresql://username:password@host:port/dbname"  # replace accordingly
engine = create_engine(db_conn_str)

# 🚀 Helper Functions

def extract_date_from_filename(filename, prefix, separator='_'):
    """
    Extract date from filename. e.g. 'CUST_MSTR_20191112.csv' → '2019-11-12'
    """
    date_str = filename.replace(prefix, '').replace('.csv', '').replace('-', '').replace('_', '')
    if separator in filename:
        date_str = filename.split(separator)[-1].replace('.csv', '')
    try:
        date_obj = datetime.strptime(date_str, "%Y%m%d")
    except:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime('%Y-%m-%d'), date_obj.strftime('%Y%m%d')

def truncate_table(table_name):
    with engine.begin() as conn:
        conn.execute(f"TRUNCATE TABLE {table_name}")

def load_to_db(df, table_name):
    truncate_table(table_name)
    df.to_sql(table_name, engine, index=False, if_exists='append')

# 📂 Read all files
for file in os.listdir(data_path):
    full_path = os.path.join(data_path, file)

    # 1️⃣ CUST_MSTR files
    if file.startswith("CUST_MSTR") and file.endswith(".csv"):
        date, _ = extract_date_from_filename(file, "CUST_MSTR_")
        df = pd.read_csv(full_path)
        df['load_date'] = date
        load_to_db(df, "CUST_MSTR")

    # 2️⃣ master_child_export files
    elif file.startswith("master_child_export") and file.endswith(".csv"):
        date, date_key = extract_date_from_filename(file, "master_child_export-")
        df = pd.read_csv(full_path)
        df['load_date'] = date
        df['date_key'] = date_key
        load_to_db(df, "master_child")

    # 3️⃣ H_ECOM_ORDER files
    elif file.startswith("H_ECOM_ORDER") and file.endswith(".csv"):
        df = pd.read_csv(full_path)
        load_to_db(df, "H_ECOM_Orders")
