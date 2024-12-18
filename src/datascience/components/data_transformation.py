import os
import pandas as pd
from src.datascience import logger
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from src.datascience.config.configuration import DataTransformationConfig

class DataTransformation:
    def __init__(self, config: DataTransformationConfig):
        self.config = config

    
    ## Note: You can add different data transformation techniques such as Scaler, PCA and all
    #You can perform all kinds of EDA in ML cycle here before passing this data to the model

    # I am only adding train_test_spliting cz this data is already cleaned up


    def train_test_spliting(self):
        data = pd.read_csv(self.config.data_path)

        ## Basic Proprocessing
        data = data.iloc[:,1:]
        scaler = StandardScaler()
        scaled_numeric_cols = scaler.fit_transform(data.iloc[:, :-1])
        le = LabelEncoder()
        encoded_last_col = le.fit_transform(data.iloc[:, -1])
        data = pd.DataFrame(scaled_numeric_cols, columns=data.columns[:-1])
        data['Species'] = encoded_last_col

        # Split the data into training and test sets. (0.75, 0.25) split.
        train, test = train_test_split(data,test_size=0.25,random_state=42)

        train.to_csv(os.path.join(self.config.root_dir, "train.csv"),index = False)
        test.to_csv(os.path.join(self.config.root_dir, "test.csv"),index = False)

        logger.info("Splited data into training and test sets")
        logger.info(train.shape)
        logger.info(test.shape)

        print(train.shape)
        print(test.shape)