import os
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config['data_ingestion']
        self.bucket_name = self.config['bucket_name']
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ration = self.config["train_ratio"]
        os.makedirs(RAW_DIR, exist_ok=True)
        logger.info(f"Data Ingestion  started with s3  bucket {self.bucket_name} and {self.file_name}")

    
    def download_csv_from_s3(self):
        try:
            
            s3_client = boto3.client('s3')
            s3_client.download_file(self.bucket_name, self.file_name, RAW_FILE_PATH)
            logger.info(f"csv file is downloaded successfully  from s3 {RAW_FILE_PATH}")
        except ClientError as e:
                       logger.error(f"AWS S3 Client Error: {e.response['Error']['Message']}")
                       raise CustomException("Failed to download csv ", e)
        
    
    def split_data(self):
        try:
            logger.info("Starting splittig process")
            data = pd.read_csv(RAW_FILE_PATH)
            train_data , test_data = train_test_split(data, test_size=1-self.train_test_ration, random_state=42)
            train_data.to_csv(TRAIN_FILE_PATH)
            test_data.to_csv(TEST_FILE_PATH)
            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")
        except Exception as e:
            logger.error("Error while splitting data")
            raise CustomException("Failed to split data into training data test sets", e)
    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.download_csv_from_s3()
            self.split_data()
            logger.info("Data Ingestion Completed successfully")
        except CustomException as e:
            logger.error(f"customException :{str(e)}")
        finally:
            logger.info("Data Ingestion Completed")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()