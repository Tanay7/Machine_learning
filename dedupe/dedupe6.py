To run this in a Jupyter Notebook effectively, we need to break the monolithic script into logical **Cells**. This allows you to inspect the data structures, check memory usage, and verify the database connection before moving to the next step.

I have also replaced `sys.exit()` commands with Python exceptions, as `sys.exit()` will kill your Jupyter Kernel and force you to restart.

### 🧱 Cell 1: Imports & Configuration

*Run this to load libraries and set up logging paths.*

```python
import os
import sys
import datetime
import logging
import configparser
import psycopg2
from psycopg2.extras import execute_values
import dedupe
import time

# ==========================================
# Configuration
# ==========================================
SETTINGS_FILE = 'PSQL_life_gi_data__learned_settings'
DB_CONFIG_FILE = 'PSQL_config_file.ini'
INPUT_TABLE = 'gi_agg_data_churn'
OUTPUT_TABLE = 'gi_agg_entity_map_churn'
LOG_DIR = 'Log_files'

# ==========================================
# Logging Setup (Optimized for Jupyter)
# ==========================================
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Clear any existing handlers to prevent duplicate logs in Jupyter
logger = logging.getLogger()
if logger.hasHandlers():
    logger.handlers.clear()

logger.setLevel(logging.INFO)

# Console Handler (Prints to Jupyter Output Cell)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info("Environment setup complete.")
```

-----

### 🧱 Cell 2: Database Connection

*Run this to test your connection. If this fails, do not proceed.*

```python
def connect_db():
    if not os.path.exists(DB_CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file {DB_CONFIG_FILE} not found.")

    config = configparser.ConfigParser()
    config.read(DB_CONFIG_FILE)
    
    settings = config['connection_settings']
    conn = psycopg2.connect(
        dbname=settings['database'],
        user=settings['username'],
        password=settings['password'],
        host=settings['hostname'],
        sslmode='require',
        connect_timeout=10
    )
    return conn, settings['schema']

try:
    connection, schema = connect_db()
    cursor = connection.cursor()
    logger.info(f"✅ Successfully connected to Schema: {schema}")
except Exception as e:
    logger.error(f"❌ Connection failed: {e}")
    # Do not proceed if this cell fails
```

-----

### 🧱 Cell 3: Fetch Data & Pre-process

*This step pulls data into memory. We print the first record to ensure the format is correct.*

```python
try:
    select_query = f"""
        SELECT id, name_only, gender, dob, address, occupation, bank_acct_no 
        FROM {schema}.{INPUT_TABLE}
    """
    logger.info(f'📥 Importing data from {INPUT_TABLE}...')
    
    t0 = time.time()
    cursor.execute(select_query)
    data = cursor.fetchall()
    
    # Get column names
    columns = tuple([d[0] for d in cursor.description])
    
    # Convert to dictionary format: {id: {col1: val1, ...}}
    data_d = {}
    for row in data:
        row_dict = dict(zip(columns, row))
        row_id = row_dict['id']
        data_d[row_id] = row_dict

    logger.info(f'✅ {len(data_d)} records imported in {round(time.time()-t0, 2)} seconds.')
    
    # Preview first item to verify structure
    first_id = list(data_d.keys())[0]
    print(f"\n👀 Data Preview (ID: {first_id}):\n", data_d[first_id])
    
    # Memory Cleanup
    del data 
    logger.info("🗑️ Raw list deleted to free memory.")

except Exception as e:
    logger.error(f"Error fetching data: {e}")
```

-----

### 🧱 Cell 4: Load Model & Run Clustering

*This is the heavy computation step. I added `%%time` to track how long the AI takes.*

```python
%%time 

# Check if settings file exists
if not os.path.exists(SETTINGS_FILE):
    raise FileNotFoundError(f"❌ Settings file '{SETTINGS_FILE}' not found. You need to train the model first.")

logger.info(f'🧠 Reading settings from {SETTINGS_FILE}...')
with open(SETTINGS_FILE, 'rb') as sf:
    deduper = dedupe.StaticDedupe(sf)

logger.info('🧩 Clustering data (threshold=0.5)... this may take a while.')

# The heavy lifting happens here
clustered_dupes = deduper.partition(data_d, threshold=0.5)

logger.info(f'✅ Clustering completed. Found {len(clustered_dupes)} sets of duplicates.')
```

-----

### 🧱 Cell 5: Write Results to DB

*This performs the Batch Insert. I added a simple progress counter so you can watch the batches load.*

```python
target_table_full = f"{schema}.{OUTPUT_TABLE}"
insert_query = f'INSERT INTO {target_table_full} (cust_id, cluster_id, cluster_score) VALUES %s'

try:
    # 1. Truncate
    logger.info(f'🧹 Truncating target table: {target_table_full}')
    cursor.execute(f'TRUNCATE TABLE {target_table_full}')

    # 2. Prepare Data
    batch_data = []
    batch_size = 10000
    total_inserted = 0
    
    logger.info('🚀 Starting batch insertion...')
    
    # Loop through clusters
    for cluster_id, (cluster_members, scores) in enumerate(clustered_dupes):            
        for cust_id, score in zip(cluster_members, scores):
            batch_data.append((int(cust_id), int(cluster_id), float(score)))

            if len(batch_data) >= batch_size:
                execute_values(cursor, insert_query, batch_data, page_size=1000)
                total_inserted += len(batch_data)
                print(f"   -> Inserted {total_inserted} rows...", end='\r') # Progress indicator
                batch_data = [] 

    # Insert remaining
    if batch_data:
        execute_values(cursor, insert_query, batch_data, page_size=1000)
        total_inserted += len(batch_data)

    print(f"\n✅ Total rows staged for commit: {total_inserted}")

except Exception as e:
    connection.rollback()
    logger.error(f"❌ Error during insertion: {e}")
    raise e
```

-----

### 🧱 Cell 6: Verify & Commit

*This is the final safety check. If the numbers match, we commit the transaction.*

```python
try:
    # Check count in DB (this counts the rows we just staged in the current transaction)
    cursor.execute(f'SELECT COUNT(*) FROM {target_table_full}')
    count_result = cursor.fetchone()[0]
    
    logger.info(f"📊 DB Count: {count_result} | Python Count: {total_inserted}")

    if count_result == total_inserted:
        connection.commit()
        logger.info('🎉 TRANSACTION COMMITTED SUCCESSFULLY!')
    else:
        logger.error('⚠️ Row count mismatch! Transaction NOT committed. Check logs.')
        # We do NOT commit here to be safe
        
except Exception as e:
    logger.error(f"Error during verification: {e}")

finally:
    if cursor: cursor.close()
    if connection: connection.close()
    logger.info('🔌 Database connection closed.')
```