import os
import joblib
import lightgbm as lgb

from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from src.logger import get_logger
from src.custom_exception import CustomException

from config.path_config import *
from config.model_params import *

from utils.common_functions import load_data

import mlflow
import mlflow.lightgbm


logger = get_logger(__name__)


class ModelTraining:

    def __init__(self, train_path, test_path, model_output_path):

        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path

        self.param_dist = LIGHTGBM_PARAMS
        self.random_search_params = RANDOM_SEARCH_PARAMS


    def load_and_split_data(self):

        try:

            logger.info(
                f"Loading training data from {self.train_path}"
            )

            train_df = load_data(self.train_path)


            logger.info(
                f"Loading testing data from {self.test_path}"
            )

            test_df = load_data(self.test_path)


            X_train = train_df.drop(
                columns=["booking_status"]
            )

            y_train = train_df["booking_status"]


            X_test = test_df.drop(
                columns=["booking_status"]
            )

            y_test = test_df["booking_status"]


            logger.info(
                "Data loaded successfully"
            )


            return X_train, y_train, X_test, y_test


        except Exception as e:

            logger.error(
                f"Error while loading data: {e}"
            )

            raise CustomException(
                "Failed to load data",
                e
            )



    def train_lgbm(self, X_train, y_train):

        try:

            logger.info(
                "Initializing LightGBM model"
            )


            lgbm_model = lgb.LGBMClassifier(
                random_state=self.random_search_params["random_state"]
            )


            random_search = RandomizedSearchCV(

                estimator=lgbm_model,

                param_distributions=self.param_dist,

                n_iter=self.random_search_params["n_iter"],

                cv=self.random_search_params["cv"],

                n_jobs=self.random_search_params["n_jobs"],

                verbose=self.random_search_params["verbose"],

                random_state=self.random_search_params["random_state"],

                scoring=self.random_search_params["scoring"]

            )


            logger.info(
                "Starting hyperparameter tuning"
            )


            random_search.fit(
                X_train,
                y_train
            )


            logger.info(
                "Hyperparameter tuning completed"
            )


            logger.info(
                f"Best Parameters: {random_search.best_params_}"
            )


            return random_search.best_estimator_



        except Exception as e:

            logger.error(
                f"Error while training model: {e}"
            )

            raise CustomException(
                "Failed to train model",
                e
            )



    def evaluate_model(self, model, X_test, y_test):

        try:

            logger.info(
                "Evaluating model"
            )


            y_pred = model.predict(X_test)


            accuracy = accuracy_score(
                y_test,
                y_pred
            )


            precision = precision_score(
                y_test,
                y_pred,
                zero_division=0
            )


            recall = recall_score(
                y_test,
                y_pred,
                zero_division=0
            )


            f1 = f1_score(
                y_test,
                y_pred,
                zero_division=0
            )


            metrics = {

                "accuracy": accuracy,

                "precision": precision,

                "recall": recall,

                "f1_score": f1

            }


            logger.info(
                f"Metrics: {metrics}"
            )


            return metrics



        except Exception as e:

            logger.error(
                f"Error while evaluating model: {e}"
            )

            raise CustomException(
                "Failed to evaluate model",
                e
            )



    def save_model(self, model):

        try:

            logger.info(
                "Saving model"
            )


            os.makedirs(
                os.path.dirname(
                    self.model_output_path
                ),
                exist_ok=True
            )


            joblib.dump(
                model,
                self.model_output_path
            )


            logger.info(
                f"Model saved at {self.model_output_path}"
            )


        except Exception as e:

            logger.error(
                f"Error while saving model: {e}"
            )

            raise CustomException(
                "Failed to save model",
                e
            )



    def run(self):

        try:

            with mlflow.start_run():


                logger.info(
                    "Starting model training pipeline"
                )


                X_train, y_train, X_test, y_test = (
                    self.load_and_split_data()
                )


                best_model = self.train_lgbm(
                    X_train,
                    y_train
                )


                metrics = self.evaluate_model(
                    best_model,
                    X_test,
                    y_test
                )


                self.save_model(
                    best_model
                )


                # MLflow logging

                mlflow.log_params(
                    best_model.get_params()
                )


                mlflow.log_metrics(
                    metrics
                )


                mlflow.log_artifact(
                    self.model_output_path
                )


                # Correct LightGBM logging
                mlflow.lightgbm.log_model(
                    best_model,
                    name="model"
                )


                logger.info(
                    "Model training completed successfully"
                )



        except Exception as e:

            logger.error(
                f"Error in model training pipeline: {e}"
            )

            raise CustomException(
                "Failed during model training pipeline",
                e
            )



if __name__ == "__main__":


    trainer = ModelTraining(

        PROCESSED_TRAIN_FILE_PATH,

        PROCESSED_TEST_FILE_PATH,

        MODEL_OUTPUT_PATH
    
    )


    trainer.run()