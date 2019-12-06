import logging
from typing import Any, Dict, List

from hypermodel import hml
from hypermodel.hml import hml_app, model_container
from hypermodel.platform.local import services
from hypermodel.platform.local.config import TstConfig
from hypermodel.tests.utilities import data_frame_utility, general
from xgboost import XGBClassifier
import os

def check_attributes_in_object(obj,dict_expected_values)->(bool,List[str]):
    """ 
    Takes a class object and a dictionary(key=attribute name, value=value expected in object instance)

    Args:
        obj(object): The instance of the class that needs to checked for.
        dict_expected_values(Dict): The dictionary has key=attribute name, value=value expected in object instance
    
    Returns:
        bool: True if all the attributes passed in dict_expected_values (as keys) are in the object
        List[str]: The list of attributes found that do not exist in the dict_expected_values list but found to exist in the class

    """
    retBool=True
    retLst=[]
    actual_dict=obj.__dict__
    if set(actual_dict) == set(dict_expected_values.keys()):
        retBool=True
    else:
        expected_keys=dict_expected_values.keys()

        for att in expected_keys:
            if att not in actual_dict:
                logging.info(f"The attribute {att} could not be found in the actual object.")
                retBool=False
                break

        for att in actual_dict:
            if att not in expected_keys:
                retLst.append(att)
    return retBool,retLst


def compare_dictionaries_equal(dict1:Dict[str,Any],dict2:Dict[str,Any]): 
    list_keys1=list(dict1.keys())
    list_keys2=list(dict2.keys())
    eqls=True
    if set(list_keys1)==set(list_keys2):
    	eqls=True
    	for k1 in list_keys1:
    		try:
    			val1=dict1[k1]
    			val2=dict2[k1]
    			if isinstance(val1,list):
    				if set(val1)!=set(val2):
    					eqls=False
    					break
    		except:
    			eqls=False
    			break
    else :
    	eqls=False

    return eqls

def get_instance_of_Model()->Any:
    classifier = XGBClassifier()
    df,numDict,catDict,tarDict=data_frame_utility.get_numerical_categorical_dataframe()
    num_columns=list(numDict.keys())    
    cat_columns=list(catDict.keys())    
    tar_columns=list(tarDict.keys())    
    model = classifier.fit(df[num_columns], df[tar_columns[0]], verbose=True)
    # model_path = self.get_local_path(self.filename_model)
    # joblib.dump(self.model, model_path)
    # return model_path
    return model

def get_instance_of_ModelContainer()->(hml.ModelContainer,Dict[str,Any]):
    tempDF,numDict,catDict,tarDict=data_frame_utility.get_numerical_categorical_dataframe(row_count=1)
    
    attr={
        "name":"test",
        "project_name":"MyProject",
        "features_numeric":list(numDict.keys()),
        "features_categorical":list(catDict.keys()),
        "target":list(tarDict.keys())[0],
        "services":services.LocalPlatformServices(),
        "features_all":list(numDict.keys())+list(catDict.keys()),
        "filename_distributions":"distribution.json",
        "filename_model":"model.joblib",
        "filename_reference":"finaname_reference.json",
        "is_loaded":False
    }


    model_cont = model_container.ModelContainer(
        name=attr["name"],
        project_name=attr["project_name"],
        features_numeric=attr["features_numeric"],
        features_categorical=attr["features_categorical"],
        target=attr["target"],
        services=attr["services"]
    )

    # tstConfig=TstConfig()
    # model_cont.filename_distributions=os.path.join(tstConfig.get_temperory_file_folder(),"test-distributions.json")
    # model_cont.filename_model=os.path.join(tstConfig.get_temperory_file_folder(),"test.joblib")
    # model_cont.filename_reference=os.path.join(tstConfig.get_temperory_file_folder(),"test-reference.json")
    model_cont.filename_distributions="test-distributions.json"
    model_cont.filename_model="test.joblib"
    model_cont.filename_reference="test-reference.json"

    return model_cont, attr



def get_filename_from_path(path):
    indx=max(path.rfind('\\'),path.rfind('/')    )

    return path[indx+1:len(path)]



def get_instance_of_HmlApp():
    attr={
        "name":"test",
        "platform":"local",
        "image_url":"Some URL",
        "package_entrypoint":"PackageEntrypoint",
        "inference":3000,
        "models":dict(),
        "services":services.LocalPlatformServices()
    }

    obj=hml_app.HmlApp(
        name=attr["name"],
        platform=attr["platform"],
        image_url=attr["image_url"],
        package_entrypoint=attr["package_entrypoint"],
        inference_port=attr["inference"],
        k8s_namespace="k8s_namespace" )
    return obj,attr
