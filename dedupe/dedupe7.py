This refactored version maintains your exact logic (batch sizes, page sizes, deduplication settings) but wraps it in a **robust, professional logging framework**.

Key improvements for "Professional Debugging":

1.  **Handler Management:** Automatically clears old log handlers to prevent duplicate logs when re-running cells (a common Jupyter issue).
2.  **Tracebacks:** Uses the `traceback` library to print the exact line number and stack trace if a crash occurs.
3.  **Performance Metrics:** Logs precise execution time (seconds) for every major step.
4.  **Data Volume Logging:** Tracks exactly how many records are in memory before and after processing.

### 🧱 Cell 1: Setup & Professional Logging Configuration

*Run this cell first to initialize the environment and loggers.*

```python
import os
import sys
import datetime
import logging
import configparser
import time
import traceback
import psycopg2
from psycopg2.extras import execute_values
import dedupe

# ==========================================
# ⚙️ Global Configuration
# ==========================================
SETTINGS_FILE = 'PSQL_life_gi_data__learned_settings'
DB_CONFIG_FILE = 'PSQL_config_file.ini'
INPUT_TABLE = 'gi_agg_data_churn'
OUTPUT_TABLE = 'gi_agg_entity_map_churn'
LOG_DIR = 'Log_files'

# ==========================================
# 🛠️ Professional Logging Setup
# ==========================================
def setup_logger():
    """Re-initializes logger to avoid duplicate outputs in Jupyter."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    log_file = os.path.join(LOG_DIR, f'Dedupe_Life_GI_{timestamp}.log')

    # Get root logger
    logger = logging.getLogger()
    
    # ⚠️ CRITICAL: Remove existing handlers to prevent log duplication in Notebooks
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.setLevel(logging.DEBUG) # Capture everything, filter in handlers

    # 1. File Handler (Detailed with timestamps)
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    f_formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(funcName)s - %(message)s')
    fh.setFormatter(f_formatter)
    logger.addHandler(fh)

    # 2. Console Handler (Clean for Jupyter output)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    c_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S')
    ch.setFormatter(c_formatter)
    logger.addHandler(ch)

    return logger, log_file

# Initialize
logger, log_filepath = setup_logger()
logger.info("✅ Environment initialized.")
logger.info(f"📁 Log file created at: {log_filepath}")
```

-----

### 🧱 Cell 2: Robust Database Connection

*Includes connection testing and masked logging for security.*

```python
def connect_db():
    if not os.path.exists(DB_CONFIG_FILE):
        logger.critical(f"❌ Configuration file {DB_CONFIG_FILE} is missing.")
        raise FileNotFoundError(f"{DB_CONFIG_FILE} not found.")

    config = configparser.ConfigParser()
    config.read(DB_CONFIG_FILE)
    
    try:
        settings = config['connection_settings']
        
        # Log connection attempt (Masking password)
        logger.info(f"🔌 Connecting to DB: Host={settings.get('hostname')}, DB={settings.get('database')}, User={settings.get('username')}")
        
        conn = psycopg2.connect(
            dbname=settings['database'],
            user=settings['username'],
            password=settings['password'],
            host=settings['hostname'],
            sslmode='require',
            connect_timeout=10
        )
        return conn, settings['schema']
        
    except Exception as e:
        logger.critical("❌ Database Connection Failed.")
        logger.debug(traceback.format_exc()) # Log full trace to file only
        raise e

# Initialize Connection
try:
    connection, schema = connect_db()
    cursor = connection.cursor()
    logger.info(f"✅ Connection successful. Target Schema: '{schema}'")
except Exception as e:
    logger.error("Stop. Fix connection issues before proceeding.")
```

-----

### 🧱 Cell 3: Data Ingestion (with Timing)

*Tracks fetch time and row counts.*

```python
try:
    t_start = time.time()
    
    select_query = f"""
        SELECT id, name_only, gender, dob, address, occupation, bank_acct_no 
        FROM {schema}.{INPUT_TABLE}
    """
    logger.info(f'📥 Executing fetch query on {INPUT_TABLE}...')
    
    cursor.execute(select_query)
    data = cursor.fetchall()
    
    fetch_time = time.time() - t_start
    logger.info(f"⏱️  Query finished in {fetch_time:.2f} seconds. Rows fetched: {len(data):,}")

    # Process into Dictionary
    logger.debug("Converting rows to dictionary format...")
    columns = tuple([d[0] for d in cursor.description])
    data_d = {}
    
    for row in data:
        row_dict = dict(zip(columns, row))
        row_id = row_dict['id']
        data_d[row_id] = row_dict

    # Free memory
    del data
    
    logger.info(f"✅ Data processed into dictionary. Total Records: {len(data_d):,}")

except Exception as e:
    logger.error(f"❌ Error during data fetching: {e}")
    logger.debug(traceback.format_exc())
```

-----

### 🧱 Cell 4: Deduplication Logic

*Includes checks for the settings file and logs the start/end of the heavy calculation.*

```python
%%time
# The %%time magic command above gives you cell execution time in Jupyter

try:
    if not os.path.exists(SETTINGS_FILE):
        logger.critical(f"❌ Settings file '{SETTINGS_FILE}' NOT FOUND.")
        logger.error("Please run the training script to generate the settings file first.")
        raise FileNotFoundError("Missing Dedupe Settings File")

    logger.info(f'🧠 Loading model from {SETTINGS_FILE}...')
    with open(SETTINGS_FILE, 'rb') as sf:
        deduper = dedupe.StaticDedupe(sf)

    logger.info('🧩 Starting Clustering (Threshold=0.5)...')
    logger.info('   (This operation is CPU intensive, please wait...)')
    
    t_cluster_start = time.time()
    
    # Run Partition
    clustered_dupes_gen = deduper.partition(data_d, threshold=0.5)
    
    # Convert generator to list to get count and allow iteration
    clustered_dupes = list(clustered_dupes_gen)
    
    duration = time.time() - t_cluster_start
    logger.info(f"✅ Clustering finished in {duration:.2f} seconds.")
    logger.info(f"📊 Found {len(clustered_dupes):,} sets of duplicates.")

except Exception as e:
    logger.error("❌ Error during clustering.")
    logger.debug(traceback.format_exc())
    raise e
```

-----

### 🧱 Cell 5: Batch Insertion (High Observability)

*Includes a calculation of the total work to be done and updates progress in real-time.*

```python
target_table_full = f"{schema}.{OUTPUT_TABLE}"
insert_query = f'INSERT INTO {target_table_full} (cust_id, cluster_id, cluster_score) VALUES %s'

try:
    # 1. Truncate
    logger.info(f'🧹 Truncating target table: {target_table_full}')
    cursor.execute(f'TRUNCATE TABLE {target_table_full}')

    # 2. Pre-calculation for Progress Bar
    # We calculate total rows to be inserted to show a % progress
    total_records_to_insert = sum(len(cluster) for cluster, scores in clustered_dupes)
    logger.info(f"🚀 Preparing to insert {total_records_to_insert:,} records into DB.")

    batch_data = []
    batch_size = 10000 # Keeping your preferred batch size
    total_inserted = 0
    start_insert_time = time.time()

    # 3. Execution Loop
    for cluster_id, (cluster_members, scores) in enumerate(clustered_dupes):            
        for cust_id, score in zip(cluster_members, scores):
            batch_data.append((int(cust_id), int(cluster_id), float(score)))

            if len(batch_data) >= batch_size:
                # Execute Batch
                execute_values(cursor, insert_query, batch_data, page_size=1000)
                
                # Update Counters
                total_inserted += len(batch_data)
                batch_data = [] # Clear list
                
                # Log Progress (Overwrites the line in Jupyter for a clean look)
                percent = (total_inserted / total_records_to_insert) * 100
                print(f"   ⏳ Progress: {total_inserted:,} / {total_records_to_insert:,} ({percent:.1f}%)", end='\r')

    # 4. Insert Cleanup (Remaining records)
    if batch_data:
        execute_values(cursor, insert_query, batch_data, page_size=1000)
        total_inserted += len(batch_data)
        print(f"   ⏳ Progress: {total_inserted:,} / {total_records_to_insert:,} (100.0%)")

    total_time = time.time() - start_insert_time
    logger.info(f"✅ Batch Insert complete. Time: {total_time:.2f}s")
    logger.info(f"📈 Average Speed: {int(total_inserted/total_time):,} rows/sec")

except Exception as e:
    connection.rollback()
    logger.critical(f"❌ Insert failed: {e}")
    logger.debug(traceback.format_exc())
    raise e
```

-----

### 🧱 Cell 6: Verification & Commit

*Final logic check with detailed result logging.*

```python
try:
    logger.info("🔍 Verifying row counts...")
    
    cursor.execute(f'SELECT COUNT(*) FROM {target_table_full}')
    db_count = cursor.fetchone()[0]
    
    logger.info(f"   Python Counter: {total_inserted:,}")
    logger.info(f"   DB Row Count:   {db_count:,}")

    if db_count == total_inserted:
        connection.commit()
        logger.info("🎉 SUCCESS: Transaction Committed.")
        logger.info("==========================================")
        logger.info("          PROCESS COMPLETED               ")
        logger.info("==========================================")
    else:
        logger.error("⚠️ MISMATCH DETECTED. Transaction NOT committed.")
        logger.error("   Check the log file for details.")
        connection.rollback()

except Exception as e:
    connection.rollback()
    logger.error(f"❌ Error during verification: {e}")
    logger.debug(traceback.format_exc())

finally:
    if cursor: cursor.close()
    if connection: connection.close()
    logger.info('🔌 Database connection closed.')
```