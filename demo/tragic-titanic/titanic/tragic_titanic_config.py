import requests
import os
import numpy as np

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
        remFile = requests.get(url, allow_redirects=True)
        open(defaultLocalFile, 'wb').write(remFile.content)
    except :
        logging.info(f"Could not download remote file from {url}, attempting to look for local file.")

    num_lines = sum(1 for line in open(defaultLocalFile))
    test_indexes=[int(i) for i in np.random.uniform(low=2, high=num_lines-1, size=(int(num_lines*TEST_DATA_RATIO),))]
    currentWorkingDir=os.getcwd()     
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





get_create_data()
