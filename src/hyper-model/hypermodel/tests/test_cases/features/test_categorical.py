from hypermodel.features import categorical
from hypermodel.tests.utilities import data_frame_utility

from typing import List, Dict

def test_get_unique_feature_values()->None:
    dataFrame=data_frame_utility.get_test_dataframe()
    features=data_frame_utility.get_test_dataframe_feature_names()
    retVal:Dict[str, List[str]]=categorical.get_unique_feature_values(dataFrame,features)
    for feat in features:
        testValue=data_frame_utility.get_unique_values(dataFrame[feat])
        assert data_frame_utility.are_lists_equal(retVal[feat],testValue)  , f"The feature {feat} does not have the expected values. The compared  are  {retVal[feat]} \n and  \n {testValue}"


def test_one_hot_encode()->None:
    dataFrame=data_frame_utility.get_test_dataframe()
    #The zero index based column list
    # the index of the features CRED_LIC_STATUS,  CRED_LIC_LOCALITY,  CRED_LIC_EDRS
    # pos 5, 9, 14
    #  
    one_hot_encode_features_positions=['CRED_LIC_STATUS',  'CRED_LIC_LOCALITY', 'CRED_LIC_EDRS']

    unique_feature_dict={}
    for feat in one_hot_encode_features_positions:
        unique_feature_dict[feat]=data_frame_utility.get_unique_values(dataFrame[feat])


    retVal=categorical.one_hot_encode(dataFrame,unique_feature_dict)

    #testing column count
    expected_value=sum([ len(unique_feature_dict[k])  for k in unique_feature_dict.keys()])
    actual_value=len(retVal.columns)
    assert actual_value==expected_value , f"Expected {expected_value} got {actual_value}"



    #testing column Names and values returned in DF
    new_column_names=  [ str(key)+":"+str(val)     for key in unique_feature_dict.keys() for val in unique_feature_dict[key]]
    ret_column_names=retVal.columns
    for new_col in new_column_names:
        # testing column Names
        assert new_col in ret_column_names, f"The column with name {new_col} could not be found in the returned data frame."
        # testing values in column confined to 0 or 1
        col_vals=data_frame_utility.get_unique_values(retVal[new_col])
        for val in col_vals:
            assert val in [0,1]


