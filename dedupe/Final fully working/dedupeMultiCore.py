# %% [markdown]
# # 🚀 Production Dedupe Run (1.3M Records)
# *Optimized for Jupyter Notebook Execution*
#
# **Usage:**
# - Run cells sequentially.
# - Ensure `PSQL_life_gi_data__learned_settings` exists before running Cell 4.
# - Monitor the "Log_files" directory for detailed logs.

# %% [markdown]
# ### 🧱 Cell 1: Imports & Configuration
# *Run this to load libraries, set up multi-core processing, and configure logging.*

# %%
import configparser
import datetime
import logging
import os
import sys
import time

# Third-party libraries
import dedupe
import psycopg2
from psycopg2.extras import execute_values

# ==========================================
# ⚙️ Multi-core Configuration
# ==========================================
NUM_CORES = 12
# ⚠️ Critical fix for Windows: Must be set before other imports/execution
os.environ['LOKY_MAX_CPU_COUNT'] = str(NUM_CORES)

# ==========================================
# ⚙️ File & DB Configuration
# ==========================================
SETTINGS_FILE = 'PSQL_life_gi_data__learned_settings'
DB_CONFIG_FILE = 'PSQL_config_file.ini'
INPUT_TABLE = 'gi_agg_data_churn'
OUTPUT_TABLE = 'gi_agg_entity_map_churn'
LOG_DIR = 'Log_files'

# ==========================================
# 📝 Logging Setup (Jupyter Optimized)
# ==========================================
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Clear any existing handlers to prevent duplicate logs in Jupyter cells
logger = logging.getLogger()
if logger.hasHandlers():
    logger.handlers.clear()

logger.setLevel(logging.INFO)

# Console Handler (Prints to Jupyter Output Cell)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# File Handler (Keeps a permanent record)
log_filename = os.path.join(
    LOG_DIR, f"Dedupe_Run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)
fh = logging.FileHandler(log_filename)
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info(f"✅ Environment setup complete. Using {NUM_CORES} CPU cores.")
logger.info(f"📄 Logging to: {log_filename}")


# %% [markdown]
# ### 🧱 Cell 2: Database Connection
# *Run this to test your connection. If this fails, do NOT proceed.*

# %%
def connect_db():
    """
    Reads config file and establishes a database connection.
    Returns: (connection_object, schema_name)
    """
    if not os.path.exists(DB_CONFIG_FILE):
        raise FileNotFoundError(f"❌ Configuration file {DB_CONFIG_FILE} not found.")

    config = configparser.ConfigParser()
    config.read(DB_CONFIG_FILE)

    settings = config['connection_settings']
    try:
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
        logger.error(f"Failed to connect to DB: {e}")
        raise e


# Initialize Connection
try:
    connection, schema = connect_db()
    cursor = connection.cursor()
    logger.info(f"✅ Successfully connected to Database. Schema: {schema}")
except Exception as e:
    logger.error("❌ Connection failed. Please check your VPN or config file.")
    # We raise an error here to stop execution flow in Jupyter "Run All"
    raise e


# %% [markdown]
# ### 🧱 Cell 3: Fetch Data & Pre-process
# *This pulls data into memory. We use a dictionary for fast lookups.*

# %%
try:
    # Query matching your specific table structure
    select_query = f"""
        SELECT id, name_only, gender, dob, address, occupation, bank_acct_no 
        FROM {schema}.{INPUT_TABLE}
    """
    logger.info(f'📥 Importing data from {INPUT_TABLE}...')

    t0 = time.time()
    cursor.execute(select_query)

    # Efficient fetch
    data = cursor.fetchall()

    # Get column names dynamically
    columns = tuple([d[0] for d in cursor.description])

    # Convert to dictionary format: {id: {col1: val1, ...}}
    data_d = {}
    for row in data:
        row_dict = dict(zip(columns, row))
        row_id = row_dict['id']  # Ensure 'id' is the primary key column
        data_d[row_id] = row_dict

    logger.info(f'✅ {len(data_d):,} records imported in {round(time.time() - t0, 2)} seconds.')

    # Preview first item to verify structure
    if data_d:
        first_id = list(data_d.keys())[0]
        print(f"\n👀 Data Preview (ID: {first_id}):\n", data_d[first_id])

    # Memory Cleanup: Delete the raw list to free RAM for Dedupe
    del data
    logger.info("🗑️ Raw list deleted to free memory.")

except Exception as e:
    logger.error(f"Error fetching data: {e}")
    raise e


# %% [markdown]
# ### 🧱 Cell 4: Load Model & Run Clustering
# *This is the heavy computation step. Uses `%%time` to track duration.*

# %%
# Check if settings file exists
if not os.path.exists(SETTINGS_FILE):
    raise FileNotFoundError(
        f"❌ Settings file '{SETTINGS_FILE}' not found. "
        "You need to run the Training Pipeline first."
    )

logger.info(f'🧠 Reading settings from {SETTINGS_FILE}...')
with open(SETTINGS_FILE, 'rb') as sf:
    # IMPORTANT: We pass num_cores here for parallel processing
    deduper = dedupe.StaticDedupe(sf, num_cores=NUM_CORES)

logger.info(
    f'🧩 Clustering {len(data_d):,} records (threshold=0.5)... this may take a while.'
)
t_start = time.time()

# The heavy lifting happens here
clustered_dupes = deduper.partition(data_d, threshold=0.5)

logger.info(f'✅ Clustering completed in {round(time.time() - t_start, 2)} seconds.')
logger.info(f'📊 Found {len(clustered_dupes)} sets of duplicates.')


# %% [markdown]
# ### 🧱 Cell 5: Write Results to DB (Batch Insert)
# *Writes results to `{OUTPUT_TABLE}` using efficient batching.*

# %%
target_table_full = f"{schema}.{OUTPUT_TABLE}"
insert_query = (
    f'INSERT INTO {target_table_full} (cust_id, cluster_id, cluster_score) VALUES %s'
)

try:
    # 1. Truncate Target Table
    logger.info(f'🧹 Truncating target table: {target_table_full}')
    cursor.execute(f'TRUNCATE TABLE {target_table_full}')

    # 2. Prepare Data Generator
    batch_data = []
    batch_size = 10000
    total_inserted = 0

    logger.info('🚀 Starting batch insertion...')

    # Loop through clusters
    # Format: clustered_dupes is a generator or list of tuples: ( (id1, id2), (score1, score2) )
    for cluster_id, (cluster_members, scores) in enumerate(clustered_dupes):
        for cust_id, score in zip(cluster_members, scores):
            batch_data.append((int(cust_id), int(cluster_id), float(score)))

            if len(batch_data) >= batch_size:
                execute_values(cursor, insert_query, batch_data, page_size=1000)
                total_inserted += len(batch_data)

                # Simple progress indicator for Jupyter
                print(f"   -> Inserted {total_inserted:,} rows...", end='\r')

                batch_data = []  # Reset batch

    # Insert remaining records
    if batch_data:
        execute_values(cursor, insert_query, batch_data, page_size=1000)
        total_inserted += len(batch_data)

    print(f"\n✅ Total rows staged for commit: {total_inserted:,}")

except Exception as e:
    connection.rollback()
    logger.error(f"❌ Error during insertion: {e}")
    raise e


# %% [markdown]
# ### 🧱 Cell 6: Verify & Commit
# *Final safety check. Commits only if counts match.*

# %%
try:
    # Check count in DB (this counts the rows we just staged in the current transaction)
    cursor.execute(f'SELECT COUNT(*) FROM {target_table_full}')
    count_result = cursor.fetchone()[0]

    logger.info(
        f"📊 Validation -- DB Count: {count_result} | Python Count: {total_inserted}"
    )

    if count_result == total_inserted:
        connection.commit()
        logger.info('🎉 TRANSACTION COMMITTED SUCCESSFULLY!')
    else:
        logger.error(
            '⚠️ Row count mismatch! Transaction NOT committed. Check logs.'
        )
        # We do NOT commit here to be safe
        connection.rollback()

except Exception as e:
    logger.error(f"Error during verification: {e}")
    connection.rollback()

finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    logger.info('🔌 Database connection closed.')