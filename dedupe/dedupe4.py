import os
import sys
import datetime
import logging
import configparser
import psycopg2
from psycopg2.extras import execute_values
import dedupe

# ==========================================
# Configuration & Constants
# ==========================================
SETTINGS_FILE = 'PSQL_life_gi_data__learned_settings'
DB_CONFIG_FILE = 'PSQL_config_file.ini'

INPUT_TABLE = 'gi_agg_data_churn'
OUTPUT_TABLE = 'gi_agg_entity_map_churn'

LOG_DIR = 'Log_files'

# ==========================================
# Logging Setup
# ==========================================
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
log_file = os.path.join(LOG_DIR, f'Dedupe_Life_GI_{timestamp}.log')

# Setup logger to write to both File and Console
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# File Handler
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console Handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info(f'Start time: {datetime.datetime.now()}')

# ==========================================
# Database Helper
# ==========================================
def connect_db():
    """
    Establishes a database connection using config file.
    Does NOT use autocommit for transaction safety.
    """
    if not os.path.exists(DB_CONFIG_FILE):
        logger.error(f"Configuration file {DB_CONFIG_FILE} not found.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(DB_CONFIG_FILE)
    
    try:
        settings = config['connection_settings']
        conn = psycopg2.connect(
            dbname=settings['database'],
            user=settings['username'],
            password=settings['password'],
            host=settings['hostname'],
            sslmode='require',
            connect_timeout=10
        )
        logger.info('Database connection established.')
        return conn, settings['schema']
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        sys.exit(1)

# ==========================================
# Main Execution
# ==========================================
def main():
    connection, schema = connect_db()
    cursor = connection.cursor()

    try:
        # 1. Fetch Data 💾
        # --------------------------------------------------
        select_query = f"""
            SELECT id, name_only, gender, dob, address, occupation, bank_acct_no 
            FROM {schema}.{INPUT_TABLE}
        """
        logger.info(f'Importing data from {INPUT_TABLE}...')
        
        cursor.execute(select_query)
        data = cursor.fetchall()
        
        # Get column names
        columns = tuple([d[0] for d in cursor.description])
        
        # Convert to dictionary format required by Dedupe: {id: {col1: val1, ...}}
        data_d = {}
        for row in data:
            row_dict = dict(zip(columns, row))
            row_id = row_dict['id']
            data_d[row_id] = row_dict

        logger.info(f'{len(data_d)} records imported.')
        
        # Memory Optimization: Delete raw list to free RAM
        del data 

        # 2. Load Dedupe Settings 🧠
        # --------------------------------------------------
        if os.path.exists(SETTINGS_FILE):
            logger.info(f'Reading settings from {SETTINGS_FILE}')
            with open(SETTINGS_FILE, 'rb') as sf:
                deduper = dedupe.StaticDedupe(sf)
        else:
            # StaticDedupe requires a pre-trained model file.
            logger.error(f"Settings file '{SETTINGS_FILE}' not found. Cannot proceed with deduplication.")
            sys.exit(1)

        # 3. Cluster Data
        # --------------------------------------------------
        logger.info('Clustering data (threshold=0.5)...')
        clustered_dupes = deduper.partition(data_d, threshold=0.5)
        logger.info('Clustering completed.')
        logger.info(f'{len(clustered_dupes)} duplicate sets found.')

        # 4. Write Results to Database (Batch Insert) 🚀
        # --------------------------------------------------
        target_table_full = f"{schema}.{OUTPUT_TABLE}"
        
        # TRUNCATE must be within the same transaction as INSERT
        logger.info(f'Truncating target table: {target_table_full}')
        cursor.execute(f'TRUNCATE TABLE {target_table_full}')

        insert_query = f'INSERT INTO {target_table_full} (cust_id, cluster_id, cluster_score) VALUES %s'
        
        batch_data = []
        batch_size = 10000
        total_inserted = 0

        logger.info('Starting batch insertion...')

        for cluster_id, (cluster_members, scores) in enumerate(clustered_dupes):            
            for cust_id, score in zip(cluster_members, scores):
                # Format data as tuples for execute_values
                batch_data.append((int(cust_id), int(cluster_id), float(score)))

                if len(batch_data) >= batch_size:
                    # Insert batch. Use page_size=1000 for improved performance.
                    execute_values(cursor, insert_query, batch_data, page_size=1000)
                    total_inserted += len(batch_data)
                    batch_data = [] # Reset batch

        # Insert remaining records
        if batch_data:
            execute_values(cursor, insert_query, batch_data, page_size=1000)
            total_inserted += len(batch_data)

        logger.info(f'Successfully inserted {total_inserted} records.')

        # 5. Verify & Commit ✅
        # --------------------------------------------------
        cursor.execute(f'SELECT COUNT(*) FROM {target_table_full}')
        count_result = cursor.fetchone()[0]
        
        if count_result == total_inserted:
            connection.commit() # Final commit of the TRUNCATE and all INSERTS
            logger.info('Transaction committed successfully.')
        else:
            logger.error(f'Row count mismatch! Inserted: {total_inserted}, Found in DB: {count_result}')
            # Decision: If count mismatch, still commit the data and exit with error to flag the issue.
            connection.commit() 
            sys.exit(1)

    except psycopg2.Error as db_err:
        connection.rollback() # Rollback all changes if DB error occurs
        logger.error(f"Database Error: {db_err}")
        sys.exit(1)
        
    except Exception as e:
        connection.rollback()
        logger.error(f"Unexpected Error: {e}")
        sys.exit(1)
        
    finally:
        if cursor: cursor.close()
        if connection: connection.close()
        logger.info(f'End time: {datetime.datetime.now()}')

if __name__ == "__main__":
    main()