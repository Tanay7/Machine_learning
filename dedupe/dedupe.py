import os
 #os.chdir('Y:\\Life_GI_Dedupe\\Test Scripts')
 #os.chdir('Y:\Life_GI_Dedupe\Test Scripts')
import dedupe
import dedupe.backport
from psycopg2.extras import execute_values
import base64
import configparser
import csv
import datetime
import email
import glob
import logging
import pandas as pd
import smtplib
import os
import sys
import gender_guesser.detector as gender_det
from datetime import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2
from psycopg2.extras import execute_values # [ADDED] Required for batch inserts
import dedupe
import dedupe.backport

settings_file = 'PSQL_life_gi_data__learned_settings'
input_table = 'gi_agg_data_churn'
output_table='gi_agg_entity_map_churn'
cust_match_table_temp = 'gi_cust_mtch_temp_churn'
cust_match_table = 'gi_cust_mtch_churn'
missing_gender_table='gi_missing_gender_churn'
load_input_table_sp = 'load_gi_agg_data_churn()'
update_missing_gender_sp = 'update_missing_gender_churn()'
extract_first_names_sp='extract_first_names_churn()'
update_cust_mtch_table_temp_sp = 'update_gi_cust_mtch_table_churn()'
extract_life_gi_cust_mtch_rec_sp = 'extract_gi_cust_match_records_churn()'
update_cust_check_table_sp = 'update_gi_check_table_churn()'
log_filepath='Log_files'


#Logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

log_file = log_filepath + r'\Dedupe_Life_GI_' + str(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) + '.log'

fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


logger.info('Start time: {}'.format((datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))))

def notifyuser(subject, body):
    config_email = configparser.ConfigParser()
    config_email.read('Email_config_file.ini')
    smtp = config_email['email_settings']['smtp']
    fromaddr = config_email['email_settings']['fromaddr']
    toaddr = config_email['email_settings']['toaddr']
    server = smtplib.SMTP(smtp) 
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

def connect():
    config = configparser.ConfigParser()
    config.read('PSQL_config_file.ini')
    user = config['connection_settings']['username']
    password = config['connection_settings']['password']
    host= config['connection_settings']['hostname']
    dbname = config['connection_settings']['database']
    global schema
    schema = config['connection_settings']['schema']
    logger.info('Initializing database connection:')
    logger.info('hostname: %s', host)
    logger.info('user: %s', user)
    logger.info('database: %s', dbname)
    global connection
    try:
        connection = psycopg2.connect(dbname=dbname,
                                      user=user, 
                                      password=password,
                                      sslmode='require',
                                      host=host,
                                      connect_timeout=5)
        logger.info('Successfully initialized database connection')
        connection.autocommit=True
    except psycopg2.Error as conn_err:
        logger.error(str(conn_err))
        notifyuser('PSQL connection error', str(conn_err)+ 'Check the following log file: ' + log_file)
        sys.exit(1)

def trimcolumns(df):
    """
    Trim whitespace from ends of each value across all series in dataframe
    """
    trimStrings = lambda x: x.strip() if type(x) is str else x
    return df.applymap(trimStrings)

def loadintodb(dataframe, tablename, errorfile):
    connect()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT * FROM ' + schema + '.' + tablename)
    except psycopg2.DatabaseError as table_err:
        logger.error(str(table_err))
        notifyuser('PSQL DB Table error', str(table_err) + 'Check the following log file: ' + log_file)
        sys.exit(1)

    columns = [i[0] for i in cursor.description]
    # print(columns)
    column_string = ','.join(columns).translate('"')
    insert_string = 'INSERT INTO ' + schema + '.' + tablename + ' (' + column_string + ') VALUES ('
    val_list = []
    for i in range(1, len(columns) + 1):
        val_list.append('%s')
    value_string = ','.join(val_list)
    insert_string += value_string + ')'
    cursor.execute('TRUNCATE TABLE ' + schema + '.' + tablename)
    #connection.commit()
    logger.info('Loading ' + tablename + ' table...')
    error_list = []
    for row in dataframe.itertuples(index=False, name=None):
        try:
            cursor.execute(insert_string, row)
        except:
            error_list.append(row)
    #connection.commit()         
    logger.info('Loading completed')    
    error_df = pd.DataFrame(error_list, columns=dataframe.columns)

    if len(error_df.index) != 0:
        error_df.to_csv(errorfile, index=False)
        logger.error('Error file created!')
        notifyuser('Error file created', ('Check ' + errorfile))  

    cursor.execute('SELECT COUNT(*) FROM ' + schema + '.' +  tablename)
    result_q = cursor.fetchone()
    table_nrows = int("".join(map(str, result_q)))
    df_nrows = int(len(dataframe))
    logger.info(tablename + ': '+ str(table_nrows) + ' records ' )
    
    if table_nrows == df_nrows:
        logger.info('Successfully '+ tablename +' table created')
    else:
        logger.error('Table loading error: Check ' + tablename + ' table records')
        notifyuser('PSQL DB Table loading error', ('Tablename: ' + tablename))
        cursor.close()
        connection.close()
        sys.exit(1)
        
connect()
c = connection.cursor()



CUSTOMER_SELECT="SELECT id, name_only, gender, dob, address, occupation, bank_acct_no FROM " + input_table

logger.info('Importing data from '+ input_table +' table ...')
c.execute(CUSTOMER_SELECT)
data = c.fetchall()
data_l = []
columns = tuple([d[0] for d in c.description] )
for row in data:
    data_l.append(dict(zip(columns, row)))
data_d = {}
for row in data_l:
            #clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
            row_id = (row['id'])
            data_d[row_id] = dict(row)
            
logger.info(str(len(data_d)) + ' records imported')
data_l=[]
del data

if os.path.exists(settings_file):
    logger.info('Reading from ' + settings_file)
    with open(settings_file, 'rb') as sf :
        deduper = dedupe.StaticDedupe(sf)
else:
    fields = [
        {'field' : 'name_only','variable name': 'name', 'type': 'String'},
        {'field' : 'gender','variable name': 'gender', 'type': 'String', 'has missing':True},
        {'field' : 'dob','variable name': 'dob', 'type': 'String','has missing':True},
        {'field' : 'address','variable name': 'address', 'type': 'String', 'has missing':True},
        {'field' : 'occupation','variable name': 'occupation', 'type': 'String', 'has missing':True}, 
        {'field' : 'bank_acct_no','variable name': 'bank_acct_no', 'type': 'String', 'has missing':True}
     
 ]
 

logger.info('Clustering.....')
clustered_dupes = deduper.partition(data_d, threshold=0.5)
logger.info('Clustering completed')

logger.info(str(len(clustered_dupes)) +' duplicate sets')
clustered_dupes_list=list(clustered_dupes)

#Writing Results to Entity Map table

c.execute('TRUNCATE TABLE '  + schema + '.' + output_table)

# [NOTE: The specific line 'KEY(cust_id))')' from your input appears to be syntax residue 
# from a CREATE TABLE statement or previous file corruption. I have commented it out to 
# prevent a Python syntax error.]
# KEY(cust_id))')
          
logger.info('Loading data into ' + output_table + ' table...' )

# [MODIFIED] BATCH INSERT LOGIC STARTS HERE
# Define query with VALUES %s for execute_values
insert_query = 'INSERT INTO ' + schema + '.' + output_table + ' (cust_id, cluster_id, cluster_score) VALUES %s'

batch_data = []
batch_size = 10000
total_inserted = 0

for cluster, scores in clustered_dupes_list:
    cluster_id = cluster[0]
    for cust_id, score in zip(cluster, scores):
        # Accumulate records into batch list
        batch_data.append((int(cust_id), int(cluster_id), float(score)))
        
        # Execute batch if size limit reached
        if len(batch_data) >= batch_size:
            execute_values(c, insert_query, batch_data)
            total_inserted += len(batch_data)
            batch_data = [] # Reset batch

# Insert any remaining records after the loop finishes
if batch_data:
    execute_values(c, insert_query, batch_data)
    total_inserted += len(batch_data)

logger.info(str(total_inserted) + ' records inserted via batch processing')
# [MODIFIED] BATCH INSERT LOGIC ENDS HERE

try:
    c.execute('SELECT COUNT(*) FROM '+ schema + '.' + output_table )

except psycopg2.DatabaseError as db_err_3:
        logger.error(str(db_err_3))
        notifyuser('PSQL DB error', str(db_err_3)+ 'Check the following log file: ' + log_file)
        sys.exit(1)

output_result_q=c.fetchone()
output_table_nrows=int("".join(map(str, output_result_q)))
logger.info(output_table + ' records: ' + str(output_table_nrows))

if  output_table_nrows !=0:
    logger.info('Successfully '+ output_table +' table created')
else:
    logger.error('Table loading error: Check ' + output_table  + ' table records')
    notifyuser('PSQL DB Table loading error', ('Tablename: ' + output_table ))
    sys.exit(1)

c.close()
connection.close()

logger.info('End time: {}'.format((datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))))
