from abc import ABC, abstractmethod
from hypermodel.platform.abstract.data_lake import DataLakeBase
from hypermodel.platform.local.config import LocalConfig
from hypermodel.platform.local.data_warehouse import SqliteDataWarehouse
from hypermodel.platform.local.config import LocalConfig
import sqlite3
import csv
from hypermodel.tests.utilities.sqlite_utility import get_column_names
from shutil import copyfile
import os 


class LocalDataLake(DataLakeBase):


    confg: LocalConfig

    def __init__(self, config: LocalConfig):
        self.config = config

    # The following is the rough mapping between the GCP implementation
    # and the Local implementation
    # GCP           <------->   Local
    # bucket_path   <------->   from_file_path
    # local_path    <------->   to_file_path
    # bucket_name   <------->   file_name


    def upload(self, to_file_path: str, from_file_path: str, file_name: str = None) -> bool:

        from_file=os.path.join(from_file_path,file_name)
        to_file=os.path.join(to_file_path,file_name)
        copyfile(from_file,to_file)
        return True

    
    # The following is the rough mapping between the GCP implementation
    # and the Local implementation
    # GCP                     <------->   Local
    # bucket_path             <------->   from_file_folder  this is the folder + file
    # destination_local_path  <------->   to_file_path  this is the folder + file
    # bucket_name             <------->   bucket_name This is redundand in local 

    def download(self, from_file_path: str, to_file_path: str, file_name: str = None) -> bool:
        if file_name is None:
            file_name = self.config.lake_bucket


        #local path of file so copying the file
        #from_file=os.path.join(from_file_folder,file_name)
        from_file=from_file_path
        #to_file=os.path.join(to_file_path,file_name)
        to_file=to_file_path
        copyfile(from_file,to_file)
        return True





  