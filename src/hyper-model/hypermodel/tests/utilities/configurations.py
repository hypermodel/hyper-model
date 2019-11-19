import configparser
import sys, os
import pytest
import logging 
# Append the directory in which this file exists to the
# path of the configuration file

TEST_CONFIGURATION_FILE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"configuration.txt")



@pytest.mark.skip(reason="Not a testing candidate")
class TstConfig:

    
    def __init__(self):
        self.parserConfig = configparser.ConfigParser()
        self.parserConfig.read(TEST_CONFIGURATION_FILE) 

    def convertPathConfig(self, path)->str:

        baseFolder=self.get_base_folder()
        if path.startswith("&"):
            path=path[1:len(path)]
            if "/" in path:
                strArr=path.split("/")
            else:
                strArr=path.split("\\")

            if "" in strArr:
                strArr.remove("")

            retVal=os.path.join(baseFolder,*strArr)
        else:
            retVal=path

        return retVal


    def get(self,section,configName)->str:

        retVal=None 
        try:
            conf_val=self.parserConfig[section][configName]	
            retVal=self.convertPathConfig(conf_val)
        except: # if the key is not found return None
            logging.info(f"Could not find {section}:{configName} returning None")
            retVal=None 
        return retVal
     

    def get_config_file_name(self)->str:  
        return TEST_CONFIGURATION_FILE


         

    def get_base_folder(self)->str:
        # this method needs to change if 
        # the location of this file changes
        parentOfCurrentFile=os.path.abspath(os.path.dirname(__file__))
        parentOfCurrentFile=os.path.abspath(os.path.dirname(parentOfCurrentFile))
        parentOfCurrentFile=os.path.abspath(os.path.dirname(parentOfCurrentFile))
        return parentOfCurrentFile

    def get_temperory_file_folder(self)->str:
        return self.get("FLAT_FILE_LOCATION","TEMPERORY_FILES_FOLDER")




