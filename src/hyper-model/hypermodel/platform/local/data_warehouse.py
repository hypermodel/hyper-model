import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import List
import logging
from hypermodel.model.table_schema import SqlTable, SqlColumn
from hypermodel.platform.local.config import LocalConfig
import sqlite3
import logging


class SqliteDataWarehouse(ABC):

    config: LocalConfig

    def __init__(self, config: LocalConfig):
        self.config = config


    # The following is the rough mapping between the GCP implementation
    # and the Local implementation
    # GCP           <------->       Local
    # bucket_path   <------->       csvLocation
    # dataset       <------->       dbLocation
    # table         <------->       tableName
    def import_csv(self, csvLocation: str, dbLocation: str, tableName: str) -> bool:
        """
            Returns True if successful otherwise returns False.
            Takes a csv file from a local folder from location "csvLocation" 
            Looks for a SQLLite db in the file specified in "dbLocation"
            Looks for the table names in "tableName" and puts 
            all the csv values in the table.
            Note: The table contents, if exist are overwritten. 
        """
       
       
        logging.info(f"SqliteDataWarehouse.import_csv  Entered!")

        logging.info(f"SqliteDataWarehouse.import_csv the  db location is { dbLocation}  the csv is {csvLocation}   and the table is {tableName}")
        # get reference to DB
        connection = sqlite3.connect(dbLocation)
        # make df of csv files
        dataFrame = pd.read_csv(csvLocation)

        # push df into the table specified
        # in case want to append to existing table make if_exists="append" 
        # in case want to overrite the existing table make if_exists="replace"       
        # we made a design decision to replace as these tables are meant to exist for 
        # a cycle of execution
        dataFrame.to_sql(tableName,connection,if_exists="replace")
        logging.info(f"SqliteDataWarehouse.import_csv  put csv into table {tableName} in database {dbLocation}  ")
        connection.close()
        return True

    def select_into(self, query: str, output_dataset: str, output_table: str) -> bool:
        logging.info(f"SqliteDataWarehouse.select_into Entered!")

        connection = sqlite3.connect(output_dataset)
        cur = connection.cursor()

        # drop table if it exists
        try:
            cur.execute(f"drop table {output_table}")
        except:
            logging.info(f"Table {output_table} could not be dropped. It may not exist or there may be an issue with the DB connection.")

        selectintoQuery = f"CREATE TABLE {output_table} AS {query}"

        cur.execute(selectintoQuery)

        logging.info(f"SqliteDataWarehouse.select_into  Exiting")
        connection.close()
        return True

    def dataframe_from_table(self, dbLocation: str, tableName: str) -> pd.DataFrame:
        logging.info(f"SqliteDataWarehouse.dataframe_from_table")

        # get reference to DB
        connection = sqlite3.connect(dbLocation)
        retDataFrame = pd.read_sql_query("SELECT * from "+tableName, connection)
        connection.close()
        return retDataFrame

    def dataframe_from_query(self, query: str) -> pd.DataFrame:
        logging.info(f"SqliteDataWarehouse.dataframe_from_query")
        dbLocation = self.config.default_sql_lite_db_file
        connection = sqlite3.connect(dbLocation)
        retDataFrame = pd.read_sql_query(query, connection)
        connection.close()
        return retDataFrame

    def get_table_columns(self, dbLocation: str, query: str)->List[SqlColumn]:
        dbLocation = self.config.default_sql_lite_db_file
        connection = sqlite3.connect(dbLocation)
        # confining the query to return minimum rows
        # in order to maintain perfromance
        queryInLower = query.lower()
        if not "limit" in queryInLower:
            query += " LIMIT 1"

        df = pd.read_sql_query(query, connection)

        retList = []
        for x in range(len(df.columns)):
            sqlCol = SqlColumn(df.columns[x], df.dtypes[x], True)
            retList.append(sqlCol)
        connection.close()
        return retList

    def dry_run(self, query: str) -> List[SqlColumn]:
        logging.info(f"SqliteDataWarehouse.dry_run")
        dbLocation = self.config.default_sql_lite_db_file
        retList = self.get_table_columns(dbLocation, query)
        return retList

    def table_schema(self, dbLocation: str, tableName: str) -> SqlTable:
        logging.info(f"SqliteDataWarehouse.table_schema")
        columns = self.get_table_columns(dbLocation, "select * from "+tableName+" limit 1")
        retTable = SqlTable(tableName, tableName, columns)
        return retTable





