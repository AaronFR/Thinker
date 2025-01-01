# Outputs for Base System Message

## StorageMethodology.py
```python
import os
from Data.Files.FileManagement import FileManagement
from Data.Files.S3Manager import S3Manager
from Data.Files.StorageBase import StorageBase


class StorageMethodology:
    """
    A factory class to create different storage managers based on the storage type.

    This class provides a method to select the appropriate storage manager 
    based on the 'STORAGE_TYPE' environment variable.
    """

    @staticmethod
    def select() -> StorageBase:
        """
        Get a storage manager instance based on the environment variable 'STORAGE_TYPE'.

        :raises ValueError: If an invalid storage type is specified or
                           required environment variables are not set.
        :return: An instance of StorageBase subclass either FileManagement or S3Manager.
        """
        storage_type = os.getenv("STORAGE_TYPE", "local")

        if storage_type == 'local':
            return FileManagement()
        elif storage_type == 's3':
            access_key = os.getenv("THE-THINKER-S3-STANDARD-ACCESS-KEY")
            secret_key = os.getenv("THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY")

            if not access_key or not secret_key:
                raise ValueError("AWS access keys must be defined for S3 storage.")
                
            return S3Manager(access_key, secret_key)
        else:
            raise ValueError(f"Invalid storage type specified: {storage_type}")


```

## StorageBase.py

```python
import os
from abc import ABC, abstractmethod
from mimetypes import guess_type
from typing import List, Dict, Any


class StorageBase(ABC):
    """
    Abstract base class for storage management.

    This class defines the interface for different storage methods, 
    including local file storage and cloud storage solutions.
    """

    @abstractmethod
    def save_file(self, content: str, file_path: str, overwrite: bool = False) -> None:
        """
        Save a file to the storage.

        :param content: The content to save.
        :param file_path: The path where the content should be saved, including directory structure.
        :param overwrite: Flag indicating whether to overwrite existing files.
        """
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """
        Read a file from the storage.

        :param file_path: The path of the file to read.
        :return: The content of the file as a string.
        """
        pass

    def save_yaml(self, yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Save a dictionary as a YAML file in the storage.

        :param yaml_path: The path where the YAML file should be saved.
        :param data: The dictionary to save.
        """
        pass

    def load_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """
        Load data from a YAML file in the storage.

        :param yaml_path: The path of the YAML file to load.
        :return: The loaded data as a dictionary, or an empty dictionary if the file does not exist.
        """
        pass

    @abstractmethod
    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Move a file from one path to another in the storage.

        :param current_path: The current location of the file.
        :param new_path: The new location for the file.
        """
        pass

    @abstractmethod
    def list_staged_files(self) -> List[str]:
        """
        List all files in the storage.

        :return: A list of file paths.
        """
        pass

    @abstractmethod
    def write_to_csv(self, file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Write a list of dictionaries to a CSV file in the storage.

        :param file_name: The name of the CSV file.
        :param dictionaries: The list of dictionaries to write to the file.
        :param fieldnames: The field names for the CSV header.
        """
        pass

    @abstractmethod
    def write_to_yaml(self, data: Dict[str, Any], yaml_path: str, overwrite: bool = False) -> None:
        """
        Write a dictionary as a YAML file in the storage.

        :param data: The dictionary to write.
        :param yaml_path: The path where the YAML file should be saved.
        :param overwrite: Flag indicating whether to overwrite existing files.
        """
        pass

    def add_new_user_file_folder(self, user_id: str) -> None:
        """
        Create a new file folder for a user.

        This method is not abstract because the implementation can be 
        defined in subclasses based on specific storage requirements.

        :param user_id: The ID of the user for whom the folder will be created.
        """
        pass

    @staticmethod
    def is_image_file(full_address: str) -> bool:
        """
        Check if the file at the specified address is an image file.

        :param full_address: The path of the file to check.
        :return: True if the file is an image; otherwise, False.
        """
        mime_type, _ = guess_type(full_address)
        return mime_type is not None and mime_type.startswith('image')


```

## S3Manager.py

```python
import os
import logging
import boto3
import yaml
from botocore.exceptions import ClientError
from typing import List, Dict, Any
from Data.Files.StorageBase import StorageBase
from Utilities.Constants import DEFAULT_ENCODING
from Utilities.Decorators import return_for_error


# Constants for environment variable keys
AWS_ACCESS_KEY_ID = "THE-THINKER-S3-STANDARD-ACCESS-KEY"
AWS_SECRET_ACCESS_KEY = "THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY"
AWS_BUCKET_ID = "THE-THINKER-S3-STANDARD-BUCKET-ID"


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
            aws_access_key_id=os.getenv(AWS_ACCESS_KEY_ID),
            aws_secret_access_key=os.getenv(AWS_SECRET_ACCESS_KEY)
        )

    @return_for_error(False, debug_logging=True)
    def save_file(self, content: str, file_path: str = None, overwrite: bool = False) -> bool:
        """
        Save a file to an S3 bucket.

        :param content: The content to be formatted and saved.
        :param file_path: S3 object name including folder prefix.
        :param overwrite: Whether to overwrite existing files.
        :return: True if the file was uploaded, else False.
        """
        # If not overwriting and the file exists, return early
        if not overwrite and self.check_file_exists(file_path):
            logging.info(f"File {file_path} already exists. Not overwriting.")
            return False

        self.s3_client.put_object(
            Bucket=self.get_bucket_name(),
            Key=self.convert_to_s3_path(file_path),
            Body=content
        )
        logging.info(f"File {file_path} uploaded.")
        return True

    def read_file(self, full_address: str) -> str:
        """
        Read a text file from an S3 bucket.

        :param full_address: S3 object name.
        :return: The contents of the file.
        """
        try:
            logging.info(f"Reading file {full_address}")
            if self.is_image_file(full_address):
                logging.warning(f"Attempted to read an image file: {full_address}")
                return f"[CANNOT READ IMAGE FILE: {full_address}]"

            response = self.s3_client.get_object(
                Bucket=self.get_bucket_name(),
                Key=self.convert_to_s3_path(full_address)
            )

            return response['Body'].read().decode(DEFAULT_ENCODING)
        except ClientError as e:
            logging.error(f"Failed to download {full_address}: {e}")
            return f"FAILED TO LOAD {full_address}"

    def save_yaml(self, yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Saves a dictionary to a YAML file in the specified S3 bucket.

        :param yaml_path: The key (path) to save the YAML file.
        :param data: The dictionary to save.
        """
        yaml_content = yaml.safe_dump(data)
        full_path = os.path.join("UserConfigs", yaml_path)

        self.s3_client.put_object(
            Bucket=self.get_bucket_name(),
            Key=self.convert_to_s3_path(full_path),
            Body=yaml_content,
            ContentType='application/x-yaml'
        )
        logging.info(f"YAML data saved to S3: {full_path}")

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
                Bucket=self.get_bucket_name(),
                Key=self.convert_to_s3_path(full_path)
            )
            yaml_content = response['Body'].read().decode(DEFAULT_ENCODING)
            existing_data = yaml.safe_load(yaml_content) or {}

            logging.info(f"YAML data loaded from S3: {full_path}")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logging.info(f"No existing data file found at S3: {full_path}.")
            else:
                logging.error(f"Error reading YAML file from S3: {e}")

        return existing_data

    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Move a file within the S3 bucket.

        :param current_path: The current location of the file.
        :param new_path: The new location for the file.
        """
        try:
            self.s3_client.copy_object(
                Bucket=self.get_bucket_name(),
                CopySource={'Bucket': self.get_bucket_name(), 'Key': self.convert_to_s3_path(current_path)},
                Key=self.convert_to_s3_path(new_path)
            )
            self.s3_client.delete_object(
                Bucket=self.get_bucket_name(),
                Key=self.convert_to_s3_path(current_path)
            )
            logging.info(f"Moved file from {current_path} to {new_path}.")
        except ClientError as e:
            logging.exception(f"Failed to move {current_path} to {new_path}: {e}")

    def list_staged_files(self) -> List[str]:
        """
        List files in a specific directory within the S3 bucket.

        :return: List of file names.
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.get_bucket_name(),
                Prefix=get_user_context()
            )

            files = []
            for page in pages:
                if 'Contents' in page:
                    files.extend(obj['Key'] for obj in page['Contents'])
            return files

        except ClientError as e:
            logging.error(f"Error listing staged files for user: {get_user_context()}: {e}")
            return []

    def check_directory_exists(self, directory_prefix: str) -> bool:
        """
        Check if a 'directory' exists in an S3 bucket.

        :param directory_prefix: Prefix representing the directory.
        :return: True if the directory exists, else False.
        """
        if not directory_prefix.endswith('/'):
            directory_prefix += '/'

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.get_bucket_name(),
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
                Bucket=self.get_bucket_name(),
                Key=self.convert_to_s3_path(file_key)
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logging.error(f"Error checking existence of file {file_key}: {e}")
                raise

    @staticmethod
    def convert_to_s3_path(path: str) -> str:
        """
        Converts a file system path to an Amazon S3-compatible path by replacing backslashes with forward slashes.

        :param path: The original file system path as a string.
        :return: The S3-compatible path.
        """
        return path.replace('\\', '/')

    def get_bucket_name(self) -> str:
        """
        Get the name of the S3 bucket from environment variables.

        :return: The S3 bucket name.
        """
        return os.getenv(AWS_BUCKET_ID)


if __name__ == "__main__":
    s3manager = S3Manager(
        os.getenv(AWS_ACCESS_KEY_ID),
        os.getenv(AWS_SECRET_ACCESS_KEY)
    )

    # Example usage of the S3Manager
    response = s3manager.save_file("testing 789", "test/testing.txt", overwrite=True)
    print(response)


```

## FileManagement.py

```python
import csv
import os
import logging
import shutil
import sys
import yaml
from typing import List, Dict, Any
from deprecated.classic import deprecated
from Data.Files.StorageBase import StorageBase
from Utilities.Constants import DEFAULT_ENCODING, MAX_FILE_SIZE
from Utilities.Decorators import handle_errors
from Utilities.ErrorHandler import ErrorHandler
from Utilities.Contexts import get_user_context


class MyDumper(yaml.Dumper):
    """
    Custom YAML dumper that formats multi-line strings using block style.
    """
    def represent_scalar(self, tag, value: str, style=None) -> yaml.nodes.ScalarNode:
        if '\n' in value or isinstance(value, str):
            return super().represent_scalar(tag, value, style='|')
        return super().represent_scalar(tag, value, style)


class FileManagement(StorageBase):
    """
    Class for managing files related to tasks and solutions.
    
    The file management system is intentionally inflexible to prevent
    possible prompt injection and data extraction from outside the designated data areas.
    ONLY information within the boundaries of the 'FileData' directory can be edited by the user.
    
    Todo: (Bug) tries to create a category folder even when set to S3?
    """

    file_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/FileData')
    config_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/UserConfigs')

    def __init__(self):
        ErrorHandler.setup_logging()

    def _get_data_path(self, file_path: str) -> str:
        """Constructs the complete path for the given file_name."""
        return os.path.join(self.file_data_directory, file_path)

    def _log_file_action(self, action: str, file_path: str):
        """Log the action performed on the file."""
        logging.info(f"File {action}: {file_path}")

    @staticmethod
    @handle_errors(raise_errors=True)
    def save_file(content: str, file_path: str, overwrite: bool = False) -> None:
        """
        Saves the response content to a file_name.
        
        :param content: The content to be formatted and saved.
        :param file_path: The file name with extension prefixed by the category folder id.
        :param overwrite: whether the file_name should be overwritten.
        
        :raises Exception: If the file size exceeds the limit.
        """
        if sys.getsizeof(content) > MAX_FILE_SIZE:
            raise Exception("File is far too large. 10 MB max.")
        
        data_path = FileManagement()._get_data_path(file_path)
        mode = "w" if overwrite or not os.path.exists(data_path) else "a"

        with open(data_path, mode, encoding=DEFAULT_ENCODING) as file:
            file.write(content)
            FileManagement()._log_file_action('saved' if not overwrite else 'overwritten', data_path)

    def read_file(self, full_address: str) -> str:
        """
        Read the content of a specified file.
        
        :param full_address: The file name to read, including category folder prefix.
        :return: The content of the file or an error message.
        """
        full_path = self._get_data_path(full_address)
        logging.info(f"Loading file content from: {full_path}")

        if self.is_image_file(full_address):
            logging.warning(f"Attempted to read an image file: {full_address}")
            return f"CANNOT READ IMAGE FILE: {full_address}"

        try:
            with open(full_path, 'r', encoding=DEFAULT_ENCODING) as file:
                return file.read()
        except FileNotFoundError:
            logging.exception(f"File not found: {full_address}")
            return f"FILE NOT FOUND {full_address}"
        except Exception:
            logging.exception("An unexpected error occurred while reading the file.")
            return f"FAILED TO LOAD {full_address}"

    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Move a file to a new path within the file management system.
        
        :param current_path: The path of the current file.
        :param new_path: The destination path for the file.
        """
        try:
            shutil.move(self._get_data_path(current_path), self._get_data_path(new_path))
            self._log_file_action('moved', f"{current_path} to {new_path}")
        except Exception:
            logging.exception("Failed to move local files.")

    @staticmethod
    def save_yaml(yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Saves a dictionary to a YAML file at the specified path.
        
        :param yaml_path: The path to the YAML file.
        :param data: The dictionary to save.
        """
        yaml_content = yaml.safe_dump(data)
        full_path = os.path.join(FileManagement.config_data_directory, yaml_path)
        FileManagement.save_file(yaml_content, full_path, overwrite=True)

    @staticmethod
    def load_yaml(yaml_path: str) -> Dict[str, object]:
        """
        Loads existing data from a YAML file if available.
        
        :param yaml_path: The path to the YAML file.
        :return: A dictionary containing the loaded data or an empty dictionary.
        """
        existing_data = {}
        full_path = os.path.join(FileManagement.config_data_directory, yaml_path)

        try:
            if os.path.isfile(full_path) and os.path.getsize(full_path) > 0:
                with open(full_path, 'r', encoding=DEFAULT_ENCODING) as yaml_file:
                    existing_data = yaml.safe_load(yaml_file) or {}
            else:
                logging.info(f"No existing data file found at {full_path}.")
        except (FileNotFoundError, yaml.YAMLError) as e:
            logging.error(f"Error reading YAML file: {e}")

        return existing_data

    @staticmethod
    def list_staged_files() -> List[str]:
        """
        List all files in the user's staging directory.
        
        :return: A list of staged file paths.
        """
        user_id = get_user_context()
        staging_directory = os.path.join(FileManagement.file_data_directory, user_id)

        try:
            entries = os.listdir(staging_directory)
            file_paths = [os.path.join(user_id, entry) for entry in entries
                          if os.path.isfile(os.path.join(staging_directory, entry))]

            logging.info(f"Found the following files in the user's staging directory: {file_paths}")
            return file_paths
        except FileNotFoundError:
            logging.exception(f"The directory {staging_directory} does not exist.")
            return []
        except Exception:
            logging.exception("An error occurred while listing staged files.")
            return []

    @staticmethod
    def get_numbered_string(lines: List[str]) -> str:
        """Returns a str where each line is prepended with its line-number."""
        return ''.join([f"{i + 1}: {line}" for i, line in enumerate(lines)])

    @staticmethod
    def write_to_csv(file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Writes or appends a list of dictionaries to a CSV file.
        
        :param file_name: The name of the CSV file.
        :param dictionaries: A list of dictionaries to write to the file.
        :param fieldnames: The field names for the CSV header.
        """
        logging.info(f"Data being written to CSV: {dictionaries}")
        file_path = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores', file_name)

        mode = 'a' if os.path.isfile(file_path) and os.path.getsize(file_path) > 0 else 'w'
        with open(file_path, mode=mode, newline='', encoding=DEFAULT_ENCODING) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if mode == 'w':
                writer.writeheader()

            if isinstance(dictionaries, list) and all(isinstance(item, dict) for item in dictionaries):
                writer.writerows(dictionaries)
            else:
                logging.error("Error: Data is not a list of dictionaries!")

    @deprecated("Should just use save_yaml")
    @staticmethod
    @handle_errors(raise_errors=True)
    def write_to_yaml(data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        """
        Writes the combined page data to a YAML file.
        
        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Determines if the YAML should be replaced or merely appended to.
        """
        mode = "w" if overwrite or not os.path.exists(yaml_path) else "a"
        with open(yaml_path, mode, encoding=DEFAULT_ENCODING) as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, Dumper=MyDumper, allow_unicode=True)

    @staticmethod
    def regex_refactor(target_string: str, replacement: str, file_path: str) -> None:
        """
        Replaces every instance of the target with the replacement str.
        
        :param target_string: The text to be replaced.
        :param replacement: The text to replace the target string.
        :param file_path: The file path including category prefix.
        :raises ValueError: if the rewrite operation fails.
        """
        file_content = FileManagement().read_file(file_path)
        modified_text = file_content.replace(target_string, replacement)

        if file_content == modified_text:
            logging.error(f"No matches found for the target string: {target_string}")
            raise ValueError(f"No matches found for the target string: {target_string}")

        FileManagement.save_file(modified_text, file_path)

    @staticmethod
    def add_new_user_file_folder(user_id: int) -> None:
        """
        Creates a new file staging folder for the new user.
        
        :param user_id: The new folder id to create.
        """
        new_directory = os.path.join(FileManagement.file_data_directory, str(user_id))
        os.makedirs(new_directory, exist_ok=True)


if __name__ == '__main__':
    numbered_lines = FileManagement().read_file("test/Writing.py")
    print(numbered_lines)


```


