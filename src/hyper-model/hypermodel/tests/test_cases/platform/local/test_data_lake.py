# placeholder test cases for now
from hypermodel.platform.local.services import LocalDataLake
from hypermodel.platform.local.config import LocalConfig
from hypermodel.tests.utilities.configurations import TstConfig
from hypermodel.tests.utilities import data_frame_utility, general
import os



def test_upload():
    classObj=LocalDataLake(LocalConfig())
    config=TstConfig()

    from_location=str(config.get("FLAT_FILE_LOCATION","DUMMY_FILE_LOCATION"))
    to_location=str(config.get("FLAT_FILE_LOCATION","TEMPERORY_FILES_FOLDER" ))

    file_name=general.get_filename_from_path(from_location)
    from_folder=from_location[0:len(from_location)-len(file_name)-1]
    to_folder=to_location


    # db=str(config.get("DATABASE_LOCATION","SQLITE_DB_FOR_TESTING"))
    # table=str(config.get("DATABASE_LOCATION","SQLITE_TABLE_FOR_TESTING2"))
    # csv=str(config.get("FLAT_FILE_LOCATION","CSV_DATA_FILE"))

    # retVal=classObj.upload(os.path.join(to_location,file_name),csv,table)
    retVal=classObj.upload(to_folder,from_folder,file_name)

    assert retVal==True




def test_download():
    classObj=LocalDataLake(LocalConfig())
    config=TstConfig()
    from_location=str(config.get("FLAT_FILE_LOCATION","DUMMY_FILE_LOCATION2"))
    to_folder=str(config.get("FLAT_FILE_LOCATION","TEMPERORY_FILES_FOLDER" ))

    file_name=general.get_filename_from_path(from_location)
    from_folder=from_location[0:len(from_location)-len(file_name)-1]
    to_file_path=os.path.join(to_folder,file_name)
    retVal=classObj.download(from_location,to_file_path)

    assert retVal==True


    