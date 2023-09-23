import sys
import os
import numpy as np
import pandas as pd

from dataclasses import dataclass
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object

@dataclass
class DataTransforamtionConfig:
    preprocessor_obj_file_path=os.path.join('artifacts','preprocessor.pkl')

class DataTransformation:
    def __init__(self):
        self.data_transform_config=DataTransforamtionConfig()

    def get_data_transformer_object(self):
        """
        this function is responsible for data transformation

        """
        try:
            numerical_columns = ["writing_score", "reading_score"]
            categorical_columns = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course",
            ]

            num_pipeline=Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy='median')),
                    ("scalar",StandardScaler())
                ]
            )
            cat_pipeline=Pipeline(
                steps=[
                    ("imputer",SimpleImputer(strategy='most_frequent')),
                    ("one_hot_encoder",OneHotEncoder()),
                    ("scalar",StandardScaler(with_mean=False))
                ]
            )

            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")

            preprocessor=ColumnTransformer(
                [
                    ("numerical_cat",num_pipeline,numerical_columns),
                    ("catrgorical_cat",cat_pipeline,categorical_columns)
                ]
            )

            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)

    
    def initiate_data_tranformation(self,train_path,test_path):
        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("reading the train and test data completed")
            logging.info("obtaining the preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()

            target_columns="math_score"
            numerical_columns=["writing_score", "reading_score"]

            input_feature_train_data=train_df.drop(columns=[target_columns],axis=1)
            target_feature_train_data=train_df[target_columns]

            input_feature_test_data=test_df.drop(columns=[target_columns],axis=1)
            target_feature_test_data=test_df[target_columns]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe."
            )

            input_fea_train_arr=preprocessing_obj.fit_transform(input_feature_train_data)
            input_fea_test_arr=preprocessing_obj.transform(input_feature_test_data)

            train_arr=np.c_[input_fea_train_arr,np.array(target_feature_train_data)]
            test_arr=np.c_[input_fea_test_arr,np.array(target_feature_test_data)]

            logging.info(f"Saved preprocessing object.")

            save_object(

                file_path=self.data_transform_config.preprocessor_obj_file_path,
                obj=preprocessing_obj
            )
            

            return(
                train_arr,
                test_arr,
                self.data_transform_config.preprocessor_obj_file_path,
            )


        except Exception as e:
            raise CustomException(e,sys)

            
