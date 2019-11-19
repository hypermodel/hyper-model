import os
import logging
from typing import List, Dict
import pandas as pd
import numpy as np
from hypermodel import hml
from hypermodel.features import one_hot_encode
import requests
from hypermodel.platform.gcp.services import GooglePlatformServices


MODEL_NAME = "titanic-xgb"
TARGET_COLUMN = "Survived"
# Lets just create a dict of default features so that we dont have to make
# the user specify a ton of parameters
DEFAULT_FEATURES: Dict[str,str] = {
    "Fare":"0",
    "Age":"10",
    "Pclass": "2",
    "Sex": "male",
    "Siblings/Spouses Aboard":"0",
    "Parents/Children Aboard":"0",
}



##Mayu be moved or changed later

DEFAULT_BASE_FOLDER=os.getcwd()
DB_LOCATION=os.path.join(DEFAULT_BASE_FOLDER, 'titanic_db.db')
DB_TABLE="titanic_train_table"
DB_TRAINING_TABLE="training_table"
DB_TESTING_TABLE="testing_table"
NUMERICAL_FEATURES = [
    "Fare",
    "Age",
]

CATEGORICAL_FEATURES = [
    "Pclass",
    "Sex",
    "Siblings/Spouses Aboard",
    "Parents/Children Aboard",
]

TEST_DATA_RATIO=0.2

os.environ["SQL_LITE_LOCATION"]= DB_LOCATION




# using the following conmstruct to join folder and file 
# as it helps concat folder and file by auto detecting / or \ 
# based on OS
TRAINING_CSV_LOCATION=os.path.join(DEFAULT_BASE_FOLDER,"titanic_train.csv")
TESTING_CSV_LOCATION=os.path.join(DEFAULT_BASE_FOLDER,"titanic_test.csv")

# location of data https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv


def get_create_data():
    url="https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv"
    defaultLocalFile="titanic.csv"
    try:
        logging.info(f"Attempting to download the titanic CSV from the URL {url}")
        remFile = requests.get(url, allow_redirects=True)
        logging.info(f"Downloaded the titanic CSV from the URL {url}")
        open(defaultLocalFile, 'wb').write(remFile.content)
    except Exception as e:
        logging.exception(e)
        logging.info(f"Could not download remote file from {url}, attempting to look for local file.")

    num_lines = sum(1 for line in open(defaultLocalFile))
    test_indexes=[int(i) for i in np.random.uniform(low=2, high=num_lines-1, size=(int(num_lines*TEST_DATA_RATIO),))]
    num_lines = 1 
    count=0
    train_file=open(TRAINING_CSV_LOCATION, 'wb')
    test_file=open(TESTING_CSV_LOCATION, 'wb')

    for line in open(defaultLocalFile):
        count+=1
        if count==1:
            test_file.write(str.encode(line))
            train_file.write(str.encode(line))
        elif count in test_indexes:
            #put in test file
            test_file.write(str.encode(line))
        else:
            #put in train file
            train_file.write(str.encode(line))


#initiates some of the files
get_create_data()


def titanic_model_container(app:  hml.HmlApp):
    """
        This is where we define what our model container looks like which helps
        us to track features / targets in the one place
    """
    model_container = hml.ModelContainer(
        name=MODEL_NAME,
        project_name="demo-titanic",
        features_numeric=NUMERICAL_FEATURES,
        features_categorical=CATEGORICAL_FEATURES,
        target=TARGET_COLUMN,
        services=app.services
    )
    return model_container


def build_feature_matrix(model_container, data_frame: pd.DataFrame, throw_on_missing=False):
    """
        Given an input dataframe, encode the categorical features (one-hot)
        and use the numeric features without change.  If we see a value in our
        dataframe, and "throw_on_missing" == True, then we will throw an exception
        as the mapping back to the original matrix wont make sense.
    """
    logging.info(f"build_feature_matrix: {model_container.name}")

    # Now lets do the encoding thing...
    encoded_df = one_hot_encode(
        data_frame, model_container.feature_uniques, throw_on_missing=throw_on_missing
    )

    for nf in model_container.features_numeric:
        encoded_df[nf] = data_frame[nf]

    matrix = encoded_df.values
    return matrix


