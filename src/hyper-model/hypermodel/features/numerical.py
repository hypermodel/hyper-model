
import pandas as pd
import logging
from typing import List, Dict


def scale_by_mean_stdev(dataframe: pd.DataFrame, feature: str, mean: float, stdev: float) -> pd.DataFrame:
    """
    Scale all the values in a column using a pre-sepcified mean / stdev, in place.

    Args:
        dataframe (pd.DataFrame): The dataframe to adjust values with
        feature (str): The name of the Feature column in the dataframe
        mean (float): The mean to use to scale values
        stdev (float): The standard deviation to use to scale values 

    Returns:
        The adjusted dataframe passed in
    """
    dataframe[feature] = dataframe[feature].apply(lambda x: (x-mean) / stdev)

    return dataframe


def describe_features(dataframe: pd.DataFrame, features: List[str]):
    """
    Return a dictionary keyed with the name of a feature and containing
    that features summary statistics.

    Args:
        dataframe (pd.DataFrame): The dataframe to adjust values with
        features (List[str]): The name of the features (columns in dataframe) to analyze

    Returns:
        A dictionary keyed by the feature name, containing summary statistics of
        the values of that feature.

    """
    feature_summaries = dict()
    for f in features:
        logging.info(f"Analyzing: {f}")
        feature_summaries[f] = dataframe[f].describe().to_dict()

    return feature_summaries
