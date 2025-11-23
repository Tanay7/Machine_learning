import os
#os.chdir('Y:\Life_GI_Dedupe\Test Scripts')
import sys
import logging
import datetime
import configparser
import psycopg2
import io
import dedupe
import dedupe.backport

# ==========================================
# CONFIGURATION
# ==========================================
SETTINGS_FILE = 'PSQL_life_gi_data__learned_settings'
INPUT_TABLE = 'gi_agg_data_churn'
OUTPUT_TABLE = 'gi_agg_entity_map_churn'
LOG_DIR = 'Log_files'

# ==========================================
# LOGGING SETUP
# ==========================================
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
log_file = os.path.join(LOG_DIR, f'Dedupe_Life_GI_{timestamp}.log')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Log to file
fh = logging.FileHandler(log_file)
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)

# Log to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

logger.info(f'Start time: {datetime.datetime.now()}')

# ==========================================
# DATABASE FUNCTIONS
# ==========================================
def get_connection():
    config = configparser.ConfigParser()
    config.read('PSQL_config_file.ini')
    s = config['connection_settings']
    
    conn = psycopg2.connect(
        dbname=s['database'],
        user=s['username'],
        password=s['password'],
        host=s['hostname'],
        sslmode='require',
        connect_timeout=10
    )
    conn.autocommit = True 
    return conn, s['schema']

def bulk_copy_data(cursor, data_generator, schema, table_name):
    """
    High-Performance Batch Logic:
    Streams data using an in-memory text buffer and Postgres COPY protocol.
    """
    buffer = io.StringIO()
    count = 0
    
    for row in data_generator:
        # Write tab-separated row to buffer
        buffer.write(f"{row[0]}\t{row[1]}\t{row[2]}\n")
        count += 1
        
        # Flush buffer every 5MB to optimize RAM usage
        if buffer.tell() > 1024 * 1024 * 5: 
            buffer.seek(0)
            cursor.copy_expert(f"COPY {schema}.{table_name} (cust_id, cluster_id, cluster_score) FROM STDIN", buffer)
            buffer.truncate(0)
            buffer.seek(0)

    # Flush any remaining data
    if buffer.tell() > 0:
        buffer.seek(0)
        cursor.copy_expert(f"COPY {schema}.{table_name} (cust_id, cluster_id, cluster_score) FROM STDIN", buffer)

    return count

# ==========================================
# MAIN EXECUTION
# ==========================================
def main():
    conn, schema = get_connection()
    c = conn.cursor()

    try:
        # 1. READ DATA
        logger.info(f'Importing data from {INPUT_TABLE}...')
        
        query = f"""
            SELECT id, name_only, gender, dob, address, occupation, bank_acct_no 
            FROM {schema}.{INPUT_TABLE}
        """
        c.execute(query)
        
        # Load data into Dictionary for dedupe
        columns = ['id', 'name_only', 'gender', 'dob', 'address', 'occupation', 'bank_acct_no']
        data_d = {}
        
        for row in c:
            row_dict = dict(zip(columns, row))
            # Handle NULL values immediately (convert to empty string)
            clean_row = {k: (v if v is not None else '') for k, v in row_dict.items()}
            data_d[clean_row['id']] = clean_row

        logger.info(f'{len(data_d)} records imported into memory.')

        # 2. SETUP DEDUPE
        if os.path.exists(SETTINGS_FILE):
            logger.info(f'Reading settings from {SETTINGS_FILE}')
            with open(SETTINGS_FILE, 'rb') as sf:
                deduper = dedupe.StaticDedupe(sf)
        else:
            logger.error(f"Settings file '{SETTINGS_FILE}' not found.")
            sys.exit(1)

        # 3. CLUSTERING
        logger.info('Clustering data...')
        clustered_dupes_gen = deduper.partition(data_d, threshold=0.5)

        # 4. WRITE TO DB (OPTIMIZED COPY)
        logger.info(f'Writing results to {OUTPUT_TABLE}...')

        # Create UNLOGGED table (skips WAL logging for speed)
        c.execute(f"""
            CREATE UNLOGGED TABLE IF NOT EXISTS {schema}.{OUTPUT_TABLE} (
                cust_id VARCHAR(255),
                cluster_id INT,
                cluster_score FLOAT
            );
            TRUNCATE TABLE {schema}.{OUTPUT_TABLE};
        """)

        # Generator to format data for the copy buffer
        def record_stream():
            for cluster_id, (records, scores) in enumerate(clustered_dupes_gen):
                for cust_id, score in zip(records, scores):
                    yield (str(cust_id), cluster_id, score)

        # Execute the Bulk Copy
        total_rows = bulk_copy_data(c, record_stream(), schema, OUTPUT_TABLE)
        
        logger.info(f"Successfully processed and wrote {total_rows} records.")

        # 5. VALIDATION
        c.execute(f'SELECT COUNT(*) FROM {schema}.{OUTPUT_TABLE}')
        count = c.fetchone()[0]
        
        if count == 0:
            logger.error("Output table is empty.")
        else:
            logger.info(f"Validation successful: {count} records in DB.")

    except Exception as e:
        logger.error(f"Critical Error: {str(e)}")
        # Email notification removed
        sys.exit(1)
    finally:
        c.close()
        conn.close()
        logger.info('Process complete.')

if __name__ == "__main__":
    main()
