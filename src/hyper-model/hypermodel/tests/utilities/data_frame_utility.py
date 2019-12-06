import pandas
import numpy
from pandas import DataFrame
import os.path
from hypermodel.tests.utilities import create_test_data
import logging
from hypermodel.tests.utilities.configurations import TstConfig  
from typing import List, Dict, Any
import math
import random


config=TstConfig()

def prepare_csv_file()->str:
    csvLocation=config.get("FLAT_FILE_LOCATION","CSV_DATA_FILE")
    if not os.path.exists(csvLocation):
        create_test_data.create_csv_file()
    return csvLocation

def get_test_dataframe()->pandas.DataFrame:
    return pandas.read_csv(prepare_csv_file())

def get_test_dataframe_feature_names()->List[str]:
    prepare_csv_file()
    features=[
        "REGISTER_NAME",#text
        "CRED_LIC_NUM",#int
        "CRED_LIC_NAME",#text
        "CRED_LIC_START_DT",#datetime
        "CRED_LIC_END_DT",#datetime
        "CRED_LIC_STATUS",#text
        "CRED_LIC_ABN_ACN",#int
        "CRED_LIC_AFSL_NUM",#int
        "CRED_LIC_STATUS_HISTORY",#text
        "CRED_LIC_LOCALITY",#text
        "CRED_LIC_STATE",#text
        "CRED_LIC_PCODE",#int
        "CRED_LIC_LAT",#float
        "CRED_LIC_LNG",#float
        "CRED_LIC_EDRS",#text
        "CRED_LIC_BN",#text
        "CRED_LIC_AUTHORISATIONS"#text
        ]
    return features


def get_unique_values(seris:pandas.Series)->List[str]:
    unique_list=seris.unique().tolist()

    return unique_list



def are_lists_equal(list1:List,list2:List)->bool:
    for x in list1:
        if str(x)=='nan':
            list1.remove(x)
    for x in list2:
        if str(x)=='nan':
            list2.remove(x)
    return set(list1)==set(list2)
    


def get_numerical_categorical_dataframe(row_count:int=100)->(DataFrame,Dict[str,List[Any]],Dict[str,List[Any]],Dict[str,List[Any]]):
    """
        Returns:
            DataFrame: containing numerical and categorical features
            numerical features:
            categorical features:
            target feature:

    """
    df=DataFrame()
    num_val_fet1=[1,2,3,4,5]
    num_val_fet2=[1.1,1.2,3.5,6.4,5.9]
    num_val_fet3=[1001,9011,300,6041,7811]

    cat_val_fet1=["val11","val12","val13"]
    cat_val_fet2=["val21","val22","val23","val24","val25","val26","val27","val28","val29","val20"]
    cat_val_fet3=["val31","val32"]

    target_values=['target1','target2','target3','target4']
    no_of_rows=row_count
    df["num_feature1"],df["num_feature2"],df["num_feature3"]=get_random_items_of_array(num_val_fet1,no_of_rows), get_random_items_of_array(num_val_fet2,no_of_rows),    get_random_items_of_array(num_val_fet3,no_of_rows)
    df["cat_feature1"],df["cat_feature2"],df["cat_feature3"]=get_random_items_of_array(cat_val_fet1,no_of_rows),get_random_items_of_array(cat_val_fet2,no_of_rows),get_random_items_of_array(cat_val_fet3,no_of_rows)
    df["target_feature"]=get_random_items_of_array(target_values,no_of_rows)

    dict_numerical={"num_feature1":num_val_fet1,"num_feature2":num_val_fet2,"num_feature3":num_val_fet3}
    dict_categorical={"cat_feature1":cat_val_fet1,"cat_feature2":cat_val_fet2,"cat_feature3":cat_val_fet3}
    dict_target={"target_feature":target_values}
    return df,dict_numerical,dict_categorical,dict_target


def get_random_items_of_array(array_to_choose_from,num_of_elements_to_return):
    length=len(array_to_choose_from)
    ret_arr=[array_to_choose_from[numpy.random.randint(0,length)] for x in range(num_of_elements_to_return)]
    return ret_arr

def get_numerical_test_dataframe(size:int=50):
    retDF=pandas.DataFrame()
    seed=0.59
    length=size
    retDF['col1']=[x*seed for x in range(length)]
    seed=0.73
    retDF['col2']=[x*seed for x in range(length)]
    seed=1.6
    retDF['col3']=[x*seed for x in range(length)]
    return retDF




