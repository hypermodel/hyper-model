import sqlite3
import pandas as pd
import logging
import os
from hypermodel.platform.local.config import LocalConfig
from hypermodel.tests.utilities.configurations import TstConfig
from typing import List, Dict



def execute_query(db, query):
    # check if the db file exists
    # if does not exist create it
    # otherwise the connection throws an error

    directory = os.path.dirname(db)
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        pass

    if not os.path.isfile(db):
        open(db, 'w+').close()
    else:
        pass
    
    conn = sqlite3.connect(db)
       

        
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        conn.close()
        conn = sqlite3.connect(db)
        logging.info(f"The statement {query} may not be a select statement. Trying a different way.")
        cursr = conn.cursor()
        cursr.execute(query)
        logging.info(f"The statement {query} seems to be a non-select statement and has now been executed.")
        conn.commit()

    conn.close()
    
    return None

def get_column_count(db:str,tableName:str)->int: 
    tbl_len_query_result_table:pd.DataFrame=execute_query(db,f'select * from ({tableName}) LIMIT 1')
    actual_column_count_table=len(tbl_len_query_result_table.columns)
    return actual_column_count_table

def get_row_column_count(db:str,query:str)->(int,int): 
    row_count_query_result:pd.DataFrame=execute_query(db,f'SELECT count(*) as c FROM ({query})')
    row_count=row_count_query_result.iloc[0][0]
    tbl_col_query_result:pd.DataFrame=execute_query(db,f'SELECT *  FROM ({query}) LIMIT 1')
    column_count=len(tbl_col_query_result.columns)
    return row_count, column_count

def get_column_names(db:str,tableName:str)->List[str]: 
    tbl_col_result:pd.DataFrame=execute_query(db,f'PRAGMA table_info({tableName})')
    return tbl_col_result['name'].tolist()




    


    