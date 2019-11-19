from hypermodel.features import numerical
from hypermodel.tests.utilities import data_frame_utility

from typing import List, Dict


import pandas as pd
import logging
from typing import List, Dict


def test_scale_by_mean_stdev():
    df=data_frame_utility.get_numerical_test_dataframe()
    df_to_pass=df.copy()
    df_change_here=df.copy()
    test_col='col1'

    mean=df_change_here[test_col].mean()
    stdev=df_change_here[test_col].std()

    actual_return_value=numerical.scale_by_mean_stdev(df_to_pass, test_col, mean, stdev)
    expected_value=(df[test_col]-mean)/stdev

    assert data_frame_utility.are_lists_equal(actual_return_value[test_col].tolist(),expected_value.tolist())


def test_describe_features():
    df=data_frame_utility.get_numerical_test_dataframe(size=5)
    retVal=numerical.describe_features(df, ['col1'])
    expected_value={'col1': {
        'count': 5.0, 
        'mean': 1.1800000000000002, 
        'std': 0.9328719097496719, 
        'min': 0.0, 
        '25%': 0.59, 
        '50%': 1.18, 
        '75%': 1.77, 
        'max': 2.36}}
    assert retVal==expected_value