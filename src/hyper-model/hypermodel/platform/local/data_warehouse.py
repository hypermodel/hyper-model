import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List

from hypermodel.model.table_schema import SqlTable, SqlColumn
from hypermodel.platform.local.config import LocalConfig
import sqlite3
import logging

class SqliteDataWarehouse(ABC):

    config: LocalConfig

    def __init__(self, config: LocalConfig):
        self.config = config

    def import_csv(self, csvLocation: str, dbLocation: str, tableName: str) -> bool:
        logging.info(f"SqliteDataWarehouse.import_csv  Entered!")
 
        #get reference to DB 
        connection =  sqlite3.connect(dbLocation)

        #make df of csv files
        dataFrame=pd.read_csv(csvLocation)

        # push df into the table specified
        # in case want to append to existing table make if_exists="append" 
        # in case want to overrite the existing table make if_exists="replace"
        dataFrame.to_sql(tableName,connection,if_exists="replace")
        logging.info(f"SqliteDataWarehouse.import_csv  put csv into table")
        connection.close()
        return True

    def select_into(self, query: str, output_dataset: str, output_table: str) -> bool:
        logging.info(f"SqliteDataWarehouse.select_into Entered!")

        connection =  sqlite3.connect(output_dataset)
        cur = conn.cursor()

        selectintoQuery="select # into "+output_table+" from "+query
        cur.execute(selectintoQuery)

        logging.info(f"SqliteDataWarehouse.select_into  Exiting")
        connection.close()
        return True

    def dataframe_from_table(self, dbLocation: str, tableName: str) -> pd.DataFrame:
        logging.info(f"SqliteDataWarehouse.dataframe_from_table")

        #get reference to DB 
        connection =  sqlite3.connect(dbLocation)
        retDataFrame = pd.read_sql_query("SELECT * from "+tableName, connection)
        connection.close()
        return retDataFrame

        

    def dataframe_from_query(self, query: str) -> pd.DataFrame:
        logging.info(f"SqliteDataWarehouse.dataframe_from_query")
        dbLocation=config.default_sql_lite_db_file
        connection =  sqlite3.connect(dbLocation)
        retDataFrame = pd.read_sql_query(query, connection)
        connection.close()
        return retDataFrame

    def get_table_columns(self,dbLocation: str, query: str)->List[SqlColumn]: 
        dbLocation=self.config.default_sql_lite_db_file
        connection =  sqlite3.connect(dbLocation)
        # confining the query to return minimum rows 
        # in order to maintain perfromance
        queryInLower=query.lower()
        if not "limit" in queryInLower:
            query+= " LIMIT 1"

        df = pd.read_sql_query(query, connection)

        retList=[]
        for x in range(len(df.columns)):
            sqlCol=SqlColumn(df.columns[x],df.dtypes[x],True)    
            retList.append(sqlCol)
        connection.close()
        return retList


    def dry_run(self, query: str) -> List[SqlColumn]:
        logging.info(f"SqliteDataWarehouse.dry_run")
        # client = self._get_client()

        # logging.info(f"DataWarehouse.dry_run")
        # config = QueryJobConfig()
        # config.dry_run = True
        # query_job = client.query(query, config)

        # result = query_job.result()
        # return DataWarehouse._translate_columns(result.schema)

        dbLocation=self.config.default_sql_lite_db_file
        retList=self.get_table_columns(dbLocation,query)

        # connection =  sqlite3.connect(dbLocation)
        # # confining the query to return minimum rows 
        # # in order to maintain perfromance
        # queryInLower=query.lower()
        # if not "limit" in queryInLower:
        #     query+= " LIMIT 1"

        # df = pd.read_sql_query(query, connection)

        # retList=[]
        # for x in range(len(df.columns)):
        #     sqlCol=SqlColumn(df.columns[x],df.dtypes[x],True)    
        #     retList.append(sqlCol)
        return retList





    def table_schema(self, dbLocation: str, tableName: str) -> SqlTable:
        logging.info(f"SqliteDataWarehouse.table_schema")
        # client = self._get_client()
        # bq_tbl = client.get_table(f"{dataset}.{table}")
        # columns = self._translate_columns(bq_tbl.schema)
        # tbl = SqlTable(bq_tbl.dataset_id, bq_tbl.table_id, columns)

        # print(tbl.to_sql())
        # return tbl
        #get reference to DB 
        columns=get_table_columns(dbLocation,"select * from "+tableName+" limit 1")
        #as SQL lite does not have a dataset ID and table ID using the table name for that
        retTable=SqlTable(tableName,tableName,columns)
        return retTable
    
    
    
    
    # @staticmethod
    # def _translate_columns(bq_columns: List[SchemaField]) -> List[SqlColumn]:
    #     # return [SqlColumn(c.name, c.field_type, c.is_nullable) for c in bq_columns]
    #     pass






def unit_test():
    #add test code here
    #test_import_csv()
    #test_dataframe_from_table()
    test_dry_run()

def test_import_csv():
    config = LocalConfig()
    sqlDW=SqliteDataWarehouse(config)
    dbNameLoc="titanic_db.dat"
    tableName="titanic_train_table"
    ret=sqlDW.import_csv("C:\\Amit\\hypermodel\\hyper-model\\demo\\tragic-titanic\\data\\titanic_train.csv", dbNameLoc,tableName )
    
    conn = sqlite3.connect(dbNameLoc)

    cur = conn.cursor()

    for row in cur.execute('SELECT * FROM '+tableName):
        print(row)

    conn.close()

def test_dataframe_from_table():
    config = LocalConfig()
    sqlDW=SqliteDataWarehouse(config)
    dbNameLoc="titanic_db.dat"
    tableName="titanic_train_table"
    retDataFrame=sqlDW.dataframe_from_table( dbNameLoc,tableName )
    
    print(retDataFrame.head())

    #conn.close()

def test_dry_run():
    query="SELECT * FROM titanic_train_table"
    config = LocalConfig()
    sqlDW=SqliteDataWarehouse(config)
    ret=sqlDW.dry_run(query)
    for row in ret:
        print(row)  


unit_test()