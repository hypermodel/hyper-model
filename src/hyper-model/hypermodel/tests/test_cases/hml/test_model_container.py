import os

import joblib
import json

from hypermodel.platform.local.config import TstConfig
from hypermodel.platform.local.services import LocalPlatformServices
from hypermodel.tests.utilities import data_frame_utility, general
import logging

from xgboost import XGBClassifier

def test_init():
    obj,expected_values=general.get_instance_of_ModelContainer()
    retBool,retLst=general.check_attributes_in_object(obj,expected_values)
    assert retBool


def test_analyze_distributions():
    obj,attributes=general.get_instance_of_ModelContainer()
    df,numDict,catDict,tarDict=data_frame_utility.get_numerical_categorical_dataframe(row_count=50)
    obj.analyze_distributions(df)
    actual_cat_feat_value_dict=obj.feature_uniques
    actual_feature_desc=obj.feature_summaries
    expected_feature_desc={ky:val for ky in list(numDict.keys()) for val in df[ky].describe().to_dict()}
    #comparing categorical features
    assert general.compare_dictionaries_equal(actual_cat_feat_value_dict,catDict)
    #comparing numerical features
    assert general.compare_dictionaries_equal(actual_feature_desc,expected_feature_desc)



def test_dump_distributions():
    # This is a to-do and we will see how testing of this happens
    # at the moment the method writes a file and we need to work out 
    # where the test file would be written and how it would be cleaned 
    obj,attributes=general.get_instance_of_ModelContainer()

    pass



def test_build_training_matrix():
    obj,attributes=general.get_instance_of_ModelContainer()
    df,numDict,catDict,tarDict=data_frame_utility.get_numerical_categorical_dataframe(row_count=50)
    list_of_categorical_columns=attributes["features_categorical"]
    expected_unique_value_dict=catDict
    obj.build_training_matrix(df)
    col_names_removed=list(expected_unique_value_dict.keys())
    new_added__categorical_columns=[f"{col}:{val}"   for col in col_names_removed for val in expected_unique_value_dict[col]]
    numerical_columns=list(numDict.keys())
    expected_column_count=len(numerical_columns)+len(new_added__categorical_columns)
    matrix=obj.build_training_matrix(df)

    actual_column_count=matrix.shape[1]# first row has the column names
    
    #Checking If The Column Count Matches
    assert actual_column_count==expected_column_count

    # Cant check if column names are as expected
    # Not confirming the column names as the return of "build_training_matrix" is 
    # a numpy.array

    # <To-Do> Match the excat values to be confirmed as the order of the columns 
    # is not guranteed

def create_job_lib_file():
    services=LocalPlatformServices()
    path=os.path.join(services.config.kfp_artifact_path,"test.joblib")
    model=general.get_instance_of_Model()
    retVal= joblib.dump(model, path)
    return retVal[0]
    

def create_distributions_file():
    services=LocalPlatformServices()
    path=os.path.join(services.config.kfp_artifact_path,"test-distributions.json")
    df,numDict,catDict,tarDict=data_frame_utility.get_numerical_categorical_dataframe(row_count=50)
    feature_summaries = dict()
    for f in list(numDict.keys()):
        logging.info(f"Analyzing: {f}")
        feature_summaries[f] = df[f].describe().to_dict()
    tstConfig=TstConfig()
    from_path_location=str(tstConfig.get("FLAT_FILE_LOCATION","REFERENCE_JSON_FILE_NAME"))
    # from_file_name=general.get_filename_from_path(from_path_location)
    # from_file_folder=from_path_location[0:len(from_path_location)-len(from_file_name)-1]
    
    dist_path_location=path
    file_name=general.get_filename_from_path(dist_path_location)
    #dist_path_folder=dist_path_location[0:len(dist_path_location)-len(file_name)-1]
    # to_location=str(tstConfig.get("FLAT_FILE_LOCATION","TEMPERORY_FILES_FOLDER" ))
    # to_file_name=general.get_filename_from_path(to_location)
    # to_path_folder=to_location[0:len(to_location)-len(to_file_name)-1]

    with open(path, "w") as f:
        json_obj = {
            "feature_uniques": catDict,
            "feature_summaries": feature_summaries,
        }
        json.dump(json_obj, f)
    os.environ['LAKE_BUCKET'] = file_name#general.get_filename_from_path(dist_path_folder)
    return from_path_location
    #return dist_path_folder

    

def test_load():
    #fil_nam=create_job_lib_file()
    fil_nam=create_distributions_file()
    obj,attributes=general.get_instance_of_ModelContainer()
    # tstConfig=TstConfig()
    # temp_folder=tstConfig.get_temperory_file_folder()
    #<TO-Do> keeping on hold for now
    # Will need to create a sample .joblib file and
    #fil_nam=create_job_lib_file()
    obj.load(fil_nam)
    # if no error is thrown mark as success
    #<To-Do> Maybe we can check the content of the loads in a refactoring exercise
    assert True



def test_load_distributions():
    obj,attributes=general.get_instance_of_ModelContainer()
    tstConfig=TstConfig()
    temp_folder=tstConfig.get_temperory_file_folder()
    #<TO-Do> keeping on hold for now
    # Will need to create a sample .joblib file and
    # load the 'feature_uniques' and 'feature_summaries'
    pass



    def test_publish():
        pass


    def test_dump_reference():
        pass

    def test_create_merge_request():
        pass

    def test_bind_model():
        pass

    def test_dump_model():
        pass

    def test_load_model():
        pass

    def test_get_local_path():
        pass

    def test_get_bucket_path():
        pass
