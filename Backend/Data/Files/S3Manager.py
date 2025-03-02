import logging
import os
import sys
from typing import List, Dict, Any

import boto3
import yaml
from botocore.exceptions import ClientError

from Constants.Exceptions import file_not_loaded, cannot_read_image_file
from Data.Files.StorageBase import StorageBase
from Constants.Constants import DEFAULT_ENCODING, MAX_FILE_SIZE, THE_THINKER_S3_STANDARD_BUCKET_ID
from Utilities.Contexts import get_user_context
from Utilities.Decorators import return_for_error


class S3Manager(StorageBase):
    """
    A manager for interacting with Amazon S3.

    :param aws_access_key_id: AWS access key ID.
    :param aws_secret_access_key: AWS secret access key.
    """

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str) -> None:
        """
        Initialize the S3Manager with AWS credentials.

        :param aws_access_key_id: AWS access key ID.
        :param aws_secret_access_key: AWS secret access key.
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        boto3.set_stream_logger("Boto", level=logging.INFO)

    @return_for_error(False, debug_logging=True)
    def save_file(self, content: str, file_path: str = None, overwrite: bool = False) -> bool:
        """
        Save a file to an S3 bucket.

        :param content: The content to be formatted and saved.
        :param file_path: S3 object name including folder prefix.
        :param overwrite: If True, allows overwriting existing files.
        :return: True if file was uploaded, else False.
        """
        if sys.getsizeof(content) > MAX_FILE_SIZE:
            raise Exception("File is far too large. 10 MB max.")

        # Prevent overwriting without an explicit overwrite
        if not overwrite and self.check_file_exists(file_path):
            logging.warning(f"File {file_path} already exists. Not overwriting.")
            content = self.read_file(file_path) + content

        try:
            self.s3_client.put_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(file_path),
                Body=content
            )
            logging.info(f"File {file_path} uploaded successfully.")
            return True
        except ClientError as e:
            logging.error(f"Failed to upload {file_path}: {e}")
            return False

    def read_file(self, full_address: str) -> str:
        """
        Read a text file from an S3 bucket.

        :param full_address: S3 object name.
        :return: The contents of the file or an error message.
        """
        try:
            logging.info(f"Reading file {full_address}")

            if self.is_image_file(full_address):
                logging.warning(f"Cannot read image file: {full_address}")
                return cannot_read_image_file(full_address)

            response = self.s3_client.get_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(full_address)
            )
            return response['Body'].read().decode(DEFAULT_ENCODING)
        except ClientError as e:
            logging.error(f"Failed to download {full_address}: {e}")
            return file_not_loaded(full_address)

    def save_yaml(self, yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Saves a dictionary to a YAML file in the specified S3 bucket.

        :param yaml_path: The key (path) to save the YAML file.
        :param data: The dictionary to save.
        """
        yaml_content = yaml.safe_dump(data)
        full_path = os.path.join("UserConfigs", yaml_path)

        try:
            self.s3_client.put_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(full_path),
                Body=yaml_content,
                ContentType='application/x-yaml'
            )
            logging.info(f"YAML data saved to S3: {full_path}")
        except ClientError as e:
            logging.error(f"Failed to save YAML to S3: {e}")

    def load_yaml(self, yaml_path: str) -> Dict[str, object]:
        """
        Loads existing data from a YAML file in the specified S3 bucket.

        :param yaml_path: The key (path) to the YAML file.
        :return: A dictionary containing the loaded data or an empty dictionary.
        """
        existing_data = {}
        full_path = os.path.join("UserConfigs", yaml_path)

        try:
            response = self.s3_client.get_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(full_path)
            )
            yaml_content = response['Body'].read().decode(DEFAULT_ENCODING)
            existing_data = yaml.safe_load(yaml_content) or {}

            logging.info(f"YAML data loaded from S3: {full_path}")
        except (ClientError, yaml.YAMLError) as e:
            logging.error(f"Error reading YAML file from S3: {e}")

        return existing_data

    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Moves a file from one location to another in the S3 bucket.

        :param current_path: The current S3 object key.
        :param new_path: The new S3 object key.
        """
        try:
            self.s3_client.copy_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                CopySource={'Bucket': os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                            'Key': self.convert_to_s3_path(current_path)},
                Key=self.convert_to_s3_path(new_path)
            )
            self.s3_client.delete_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(current_path)
            )
            logging.info(f"File {current_path} moved to {new_path}.")
        except ClientError as e:
            logging.error(f"FAILED TO MOVE {current_path} TO {new_path}: {e}")

    def list_files(self, category_id: str) -> List[str]:
        """
        List files in a specific directory within an S3 bucket category folder.

        NOTE: Currently unused.

        :return: List of file names.
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Prefix=category_id
            )

            files = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        files.append(obj['Key'])
            return files

        except ClientError as e:
            logging.error(f"Error listing staged files for user: {get_user_context()}: {e}")
            return []

    def write_to_csv(self, file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Writes or appends a list of dictionaries to a CSV file. (NOT IMPLEMENTED)

        :param file_name: The name of the CSV file to save to.
        :param dictionaries: The list of dictionaries to write.
        :param fieldnames: The order of the fields in the CSV.
        """
        logging.error("NOT IMPLEMENTED")
        pass

    def write_to_yaml(self, data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        """
        Writes data to a YAML file in S3. (NOT IMPLEMENTED)

        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Determines if the YAML file should be replaced or appended to.
        """
        logging.error("NOT IMPLEMENTED")
        pass

    def check_directory_exists(self, directory_prefix: str) -> bool:
        """
        Check if a 'directory' exists in an S3 bucket.

        :param directory_prefix: Prefix representing the directory.
        :return: True if directory exists, else False.
        """
        if not directory_prefix.endswith('/'):
            directory_prefix += '/'

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Prefix=directory_prefix,
                MaxKeys=1
            )
            exists = 'Contents' in response
            logging.info(f"Directory {'exists' if exists else 'does not exist'}: {directory_prefix}")
            return exists
        except ClientError as e:
            logging.error(f"Error checking directory {directory_prefix}: {e}")
            return False

    def check_file_exists(self, file_key: str) -> bool:
        """
        Check if a specific file exists in the S3 bucket.

        :param file_key: The key of the file to check for.
        :return: True if the file exists, False otherwise.
        """
        try:
            self.s3_client.head_object(
                Bucket=os.getenv(THE_THINKER_S3_STANDARD_BUCKET_ID),
                Key=self.convert_to_s3_path(file_key)
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logging.error(f"Error checking if file exists: {e}")
                raise

    def add_new_category_folder(self, category_id: str) -> None:
        """
        Add a new category file folder. (Not necessary in S3, as folders are virtual.)

        :param category_id: The ID of the new category folder.
        """
        pass

    @staticmethod
    def convert_to_s3_path(path: str) -> str:
        """
        Converts a file system path to an Amazon S3-compatible path.
        The existence of this method is terrible

        :param path: The original file system path as a string.
        :return: The S3-compatible path.
        """
        return path.replace('\\', '/')


if __name__ == "__main__":
    s3manager = S3Manager(
        os.getenv("THE-THINKER-S3-STANDARD-ACCESS-KEY"),
        os.getenv("THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY")
    )

    # Example usage
    response = s3manager.save_file("testing 789", "test/testing.txt", overwrite=True)
    print(response)
