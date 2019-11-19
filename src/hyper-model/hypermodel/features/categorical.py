"""
Helper functions for dealing with categorical features
"""

import pandas as pd
from typing import List, Dict
import numpy
import math 


def get_unique_feature_values(dataframe: pd.DataFrame, features: List[str]) -> Dict[str, List[str]]:
    """
        Take a dataframe and a list of features, and for each feature find me all the unique
    values of that feature.  This is a useful step prior to one-hot encoding, as it gives
    you a list of all the values we can expect to encode. 

    Args:
        dataframe (pd.DataFrame): The DataFrame to use to collect values
        features (List[str]): A list of all the Features we want to find the unique values of

    Returns:
        A dictionary keyed by the name of each feature, containing a list of all that features
        unique values
    """


    feature_uniques: Dict[str, List[str]] = dict()

    for feature in features:
        unique_features = dataframe[feature].unique()
        feature_uniques[feature] = unique_features.tolist()
  
    
    return feature_uniques


def one_hot_encode(dataframe: pd.DataFrame, uniques: Dict[str, List[str]], throw_on_missing=False) -> pd.DataFrame:
    """
    Create a new dataframe that one-hot-encodes values from the given dataframe
    against the known list of unique feature values (calculated using `get_unique_feature_values`).

    Args:
        dataframe (pd.DataFrame): The DataFrame to use to collect values
        uniques (Dict[str, List[str]]): A dict keyed by feature name, containing a list of unique values
        throw_on_missing (bool): If a value is found in the DataFrame which is missing from the
            `uniques` dict(), and this parameter is True, we will throw an Exception to prevent 
            further execution.  When encoding unseen data against known data, this can be useful
            to ensure you are not predicting using unseen data.
    Returns:
        A new DataFrame with each Feature/Value pair as a new column with a "1" where
        the row contains the features value, and a "0" where it does not

    """
    new_frame = pd.DataFrame()
    for feature in uniques:
        feature_value_list = uniques[feature]

        # Validate that our values are actually in our seen set
        if throw_on_missing:
            sample_uniques = dataframe[feature].unique()
            for s in sample_uniques:
                if s not in feature_value_list:
                    raise Exception(f"The value '{s}' has not been seen before in feature '{feature}', unable to one_hot_encode")


        for feature_value in feature_value_list:
            # Track a new column list that gets a "1" if it matches and "0" otherwise
            one_hot_col = (dataframe[feature] == feature_value).astype(int)
            new_frame[f"{feature}:{feature_value}"] = one_hot_col

    return new_frame
