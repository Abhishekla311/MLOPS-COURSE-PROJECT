import os
import pandas as pd
import numpy as np

from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from utils.common_functions import read_yaml, load_data

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE


logger = get_logger(__name__)


class DataProcessor:

    def __init__(self, train_path, test_path, processed_dir, config_path):

        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        os.makedirs(
            self.processed_dir,
            exist_ok=True
        )


    def preprocess_data(self, df):

        try:

            logger.info("Starting data preprocessing")


            # Remove unnecessary columns

            drop_columns = [
                "Unnamed: 0",
                "Booking_ID"
            ]


            for col in drop_columns:

                if col in df.columns:
                    df.drop(
                        columns=[col],
                        inplace=True
                    )


            # Remove duplicates

            df.drop_duplicates(
                inplace=True
            )


            cat_cols = self.config["data_preprocessing"]["categorical_columns"]

            num_cols = self.config["data_preprocessing"]["numerical_columns"]


            logger.info("Applying label encoding")


            encoder = LabelEncoder()


            for col in cat_cols:

                if col in df.columns:

                    df[col] = encoder.fit_transform(
                        df[col]
                    )


            logger.info("Handling skewness")


            skew_threshold = self.config["data_preprocessing"]["skewness_threshold"]


            for col in num_cols:

                if col in df.columns:

                    if abs(df[col].skew()) > skew_threshold:

                        df[col] = np.log1p(
                            df[col]
                        )


            return df


        except Exception as e:

            logger.error(
                f"Preprocessing error: {e}"
            )

            raise CustomException(
                "Error while preprocessing data",
                e
            )



    def balance_data(self, df):

        try:

            logger.info(
                "Applying SMOTE"
            )


            X = df.drop(
                columns=["booking_status"]
            )

            y = df["booking_status"]


            smote = SMOTE(
                random_state=42
            )


            X_resampled, y_resampled = smote.fit_resample(
                X,
                y
            )


            balanced_df = pd.DataFrame(
                X_resampled,
                columns=X.columns
            )


            balanced_df["booking_status"] = y_resampled


            logger.info(
                "SMOTE completed"
            )


            return balanced_df


        except Exception as e:

            logger.error(
                f"SMOTE error: {e}"
            )

            raise CustomException(
                "Error while balancing data",
                e
            )



    def select_features(self, df):

        try:

            logger.info(
                "Feature selection started"
            )


            X = df.drop(
                columns=["booking_status"]
            )


            y = df["booking_status"]


            model = RandomForestClassifier(
                random_state=42
            )


            model.fit(
                X,
                y
            )


            importance = pd.DataFrame({

                "feature": X.columns,

                "importance": model.feature_importances_

            })


            importance.sort_values(
                by="importance",
                ascending=False,
                inplace=True
            )


            n_features = self.config["data_preprocessing"]["no_of_features"]


            selected_features = (
                importance
                ["feature"]
                .head(n_features)
                .tolist()
            )


            logger.info(
                f"Selected features: {selected_features}"
            )


            return df[
                selected_features + ["booking_status"]
            ]


        except Exception as e:

            logger.error(
                f"Feature selection error: {e}"
            )

            raise CustomException(
                "Error while feature selection",
                e
            )



    def save_data(self, df, path):

        try:

            df.to_csv(
                path,
                index=False
            )


            logger.info(
                f"Saved file: {path}"
            )


        except Exception as e:

            raise CustomException(
                "Error while saving file",
                e
            )



    def process(self):

        try:

            logger.info(
                "Starting preprocessing pipeline"
            )


            train_df = load_data(
                self.train_path
            )


            test_df = load_data(
                self.test_path
            )


            train_df = self.preprocess_data(
                train_df
            )


            test_df = self.preprocess_data(
                test_df
            )


            train_df = self.balance_data(
                train_df
            )


            train_df = self.select_features(
                train_df
            )


            # Match test columns

            test_df = test_df[
                train_df.columns
            ]


            self.save_data(
                train_df,
                PROCESSED_TRAIN_FILE_PATH
            )


            self.save_data(
                test_df,
                PROCESSED_TEST_FILE_PATH
            )


            logger.info(
                "Data preprocessing completed successfully"
            )


        except Exception as e:

            logger.error(
                f"Pipeline error: {e}"
            )

            raise CustomException(
                "Error while data preprocessing pipeline",
                e
            )



if __name__ == "__main__":


    processor = DataProcessor(

        TRAIN_FILE_PATH,

        TEST_FILE_PATH,

        PROCESSED_DIR,

        CONFIG_PATH

    )


    processor.process()