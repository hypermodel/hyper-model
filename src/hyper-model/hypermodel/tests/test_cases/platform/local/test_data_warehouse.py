from hypermodel.tests.utilities.configurations import TstConfig
import sqlite3
from hypermodel.platform.local.data_warehouse import SqliteDataWarehouse
from hypermodel.platform.local.config import LocalConfig
from  hypermodel.tests.utilities.sqlite_utility import execute_query,get_row_column_count, get_row_column_count
from  hypermodel.tests.utilities.create_test_data import populate_table_in_database
from  hypermodel.model.table_schema import SqlTable, SqlColumn
import pandas as pd
import logging 


def helper_execute_import_csv()->bool:
    config=TstConfig()
    #get testing csv file
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING1"))
    csv=str(config.get("FLAT_FILE_LOCATION","CSV_DATA_FILE"))
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.import_csv(csv,db,table)
    return retVal


def test_import_csv_length_of_db()->None:
    config=TstConfig()
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING1"))
    expected_table_length =5129

    retVal=helper_execute_import_csv()
   
    tbl_len_query_result=execute_query(db,f'SELECT count(*) as c FROM {table}')
    actual_table_length=tbl_len_query_result.iloc[0][0]
    assert expected_table_length == actual_table_length
    

def test_import_csv_returned_true()->None:
    retVal=helper_execute_import_csv()
    assert retVal is True

def helper_execute_select_into(query)->pd.DataFrame:
    config=TstConfig()
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.select_into(query,db,table2)
    return retVal


def test_select_into_row_count()-> None:
    config=TstConfig()
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table1=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING1"))
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    # Confining to 30 as we just want to limit the size
    # The assumption is that the row count of table 1 is more than 30
    query=f"select * from {table1} LIMIT 30"
    helper_execute_select_into(query)
    row_count,col_count=get_row_column_count(db,table2)
    expected_row_count=30
    assert expected_row_count == row_count


def test_select_into_column_count()-> None:
    config=TstConfig()
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table1=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING1"))
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    # Confining to 30 as we just want to limit the size
    # The assumption is that the row count of table 1 is more than 30
    query_to_copy_into_table2=f"select * from {table1} LIMIT 30"
    helper_execute_select_into(query_to_copy_into_table2)
    row,actual_column_count_table1=get_row_column_count(db,table1)
    row,actual_column_count_table2=get_row_column_count(db,table2)
    expected_column_length=actual_column_count_table1
    assert expected_column_length == actual_column_count_table2


def helper_dataframe_from_table( dbLocation: str, tableName: str)->pd.DataFrame:
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.dataframe_from_table(dbLocation,tableName)
    return retVal

def test_dataframe_from_table_size()->None:
    config=TstConfig()
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    table1=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING1"))
    df=helper_dataframe_from_table(db,table1)
    row,actual_column_count_table1=get_row_column_count(db,table1)
    assert df.shape == (row,actual_column_count_table1)


def helper_dataframe_from_query(query: str) -> pd.DataFrame:
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.dataframe_from_query(query)
    return retVal

def test_dataframe_from_query_size()->None:
    config=TstConfig()
    localConfig=LocalConfig()
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    # query method to return method returning value
    db=localConfig.default_sql_lite_db_file
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    expected_row_count,expected_column_count= populate_table_in_database(db,table2)
    retVal=helper_dataframe_from_query(f"select * from {table2}")
    assert (expected_row_count,expected_column_count)==retVal.shape

def test_get_table_columns():
    config=TstConfig()
    localConfig=LocalConfig()
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    db=localConfig.default_sql_lite_db_file
    populate_table_in_database(db,table2)
    #populated test data in table2
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.get_table_columns(db,f"select * from {table2} ")
    testDataColumns=[]
    testDataColumns.append(SqlColumn("id", "int64", True))
    testDataColumns.append(SqlColumn("title", "object", True))
    testDataColumns.append(SqlColumn("author", "object", True))
    testDataColumns.append(SqlColumn("price", "object", True))
    testDataColumns.append(SqlColumn("year", "object", True))

    #see if all column values match
    for col in retVal:
        assert col in testDataColumns
    
    # see if all column count match
    assert  len(testDataColumns)==len(retVal)


def test_dry_run():
    config=TstConfig()
    localConfig=LocalConfig()
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    db=localConfig.default_sql_lite_db_file
    populate_table_in_database(db,table2)
    #populated test data in table2
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.dry_run(f"select * from {table2} ")
    testDataColumns=[]
    testDataColumns.append(SqlColumn("id", "int64", True))
    testDataColumns.append(SqlColumn("title", "object", True))
    testDataColumns.append(SqlColumn("author", "object", True))
    testDataColumns.append(SqlColumn("price", "object", True))
    testDataColumns.append(SqlColumn("year", "object", True))

    #see if all column values match
    for col in retVal:
        assert col in testDataColumns
    
    # see if all column count match
    assert  len(testDataColumns)==len(retVal)


def test_table_schema():
    config=TstConfig()
    table2=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    populate_table_in_database(db,table2)
    #populated test data in table2
    classObj=SqliteDataWarehouse(LocalConfig())
    retVal=classObj.table_schema(db, table2)
    testDataColumns=[]
    testDataColumns.append(SqlColumn("id", "int64", True))
    testDataColumns.append(SqlColumn("title", "object", True))
    testDataColumns.append(SqlColumn("author", "object", True))
    testDataColumns.append(SqlColumn("price", "object", True))
    testDataColumns.append(SqlColumn("year", "object", True))

    expectedTable=SqlTable(table2,table2,testDataColumns)
    
    # see if all column count match
    assert  expectedTable==retVal