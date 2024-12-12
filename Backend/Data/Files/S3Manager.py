import logging
import os
from typing import List, Dict

import boto3
from botocore.exceptions import ClientError

from Data.Files.StorageBase import StorageBase
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
        Initialize the S3Manager with AWS credentials and region.
        ToDo: consider adding region_name

        :param aws_access_key_id: AWS access key ID.
        :param aws_secret_access_key: AWS secret access key.

        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

    @return_for_error(False, debug_logging=True)
    def save_file(self, content: str, file_path: str = None, overwrite: bool = False) -> bool:
        """
        Save a file to an S3 bucket.

        :param content: The content to be formatted and saved
        :param file_path: S3 object name including folder prefix
        :param overwrite:
        :return: True if file was uploaded, else False.
        """
        if not overwrite & self.check_file_exists(file_path):
            content += self.read_file(file_path)

        self.s3_client.put_object(
            Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
            Key=file_path,
            Body=content.encode('utf-8')
        )
        logging.info(f"File {file_path} uploaded.")
        return True

    def read_file(self, full_address: str) -> str:
        """
        Read a text file from an S3 bucket.

        :param full_address: S3 object name.
        :return: The contents of the file
        """
        try:
            logging.info(f"Reading File {full_address}")

            if self.is_image_file(full_address):
                logging.warning(f"Attempted to read an image file: {full_address}")
                return f"[CANNOT READ IMAGE FILE: {full_address}]"

            response = self.s3_client.get_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                Key="textUtils.js"
            )
            return response['Body'].read()
        except ClientError as e:
            logging.error(f"Failed to download {full_address}: {e}")
            return f"[FAILED TO LOAD {full_address}]"

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
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                Prefix=directory_prefix,
                MaxKeys=1
            )
            exists = 'Contents' in response
            logging.info(f"Directory {'exists' if exists else 'does not exist'}: {directory_prefix}")
            return exists
        except ClientError as e:
            logging.error(f"Error checking directory {directory_prefix}: {e}")
            return False

    def list_staged_files(self) -> list:
        """
        List files in a specific directory within an S3 bucket.

        :return: List of file names.
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                Prefix=get_user_context()
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
        logging.error("NOT IMPLEMENTED")
        pass

    def write_to_yaml(self, data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        logging.error("NOT IMPLEMENTED")
        pass

    def check_file_exists(self, file_key: str) -> bool:
        """Check if a specific file exists in the S3 bucket.

        :param file_key: The key of the file to check for.
        :return: True if the file exists, False otherwise.
        """
        s3_client = boto3.client('s3')

        try:
            s3_client.head_object(Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"), Key=file_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise

    def add_new_user_file_folder(self, user_id):
        """
        It isn't necessary to create a 'folder' in S3, its just a part of the name
        """
        pass


if __name__ == "__main__":
    s3manager = S3Manager(
        os.getenv("THE-THINKER-S3-STANDARD-ACCESS-KEY"),
        os.getenv("THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY")
    )

    response = s3manager.save_file("testing 789", os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"), "test/testing.txt")
    print(response)
