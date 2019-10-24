from typing import List, Set, Dict, Tuple, Optional


class SqlColumn():
    """
    A simple class to model a Column in a Table within a DataWarehouse or DataMart
    """
    column_name: str
    column_type: str
    nullable: bool

    def __init__(self, column_name: str, column_type: str, nullable: bool):
        self.column_name = column_name
        self.column_type = column_type
        self.nullable = nullable

    def to_sql(self) -> str:
        """
        Generate an SQL snippet for the definition of this column.
        
        Returns:
            An SQL string with the columns definition, suitable for including in a Create Table script

        """
        null = "NULL" if self.nullable == True else "NOT NULL"

        return f"{self.column_name} {self.column_type} {null}"

    def __str__(self) -> str:
        return self.to_sql()


class SqlTable():
    """
    A simple class to model a Column in a Table within a DataWarehouse or DataMart
    """
    table_id: str
    dataset_id: str
    columns: List[SqlColumn]

    def __init__(self, dataset_id: str, table_id: str, columns: List[SqlColumn] = list()):
        self.table_id = table_id
        self.dataset_id = dataset_id
        self.columns = columns

    def to_sql(self) -> str:
        """
        Generate a "CREATE TABLE" script for the table defined in this object

        Returns:
            An SQL string with the create table script
        """
        header = f"{self.dataset_id}.{self.table_id} ("
        cols = "\n\t".join([c.to_sql() for c in self.columns])
        return f"{header}\n\t{cols}\n)"

    def __str__(self) -> str:
        return self.to_sql()
