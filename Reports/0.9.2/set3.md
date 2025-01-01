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

    ToDo: Add a check that access keys are defined for a class singleton initialization, i.e., once during deployment.
    """

    @staticmethod
    def select() -> StorageBase:
        """
        Get a storage manager instance based on the environment variable 'STORAGE_TYPE'.

        This method checks the value of the 'STORAGE_TYPE' environment variable and returns an instance
        of the appropriate storage manager (FileManagement or S3Manager). 

        :raises ValueError: If an invalid storage type is specified or
                            required environment variables are not set.

        :return: An instance of a StorageBase subclass (either FileManagement or S3Manager).
        """
        storage_type = os.getenv("STORAGE_TYPE", "local")

        if storage_type == 'local':
            return FileManagement()
        elif storage_type == 's3':
            access_key = os.getenv("THE-THINKER-S3-STANDARD-ACCESS-KEY")
            secret_key = os.getenv("THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY")

            if not access_key or not secret_key:
                raise ValueError("Both access key and secret key must be set for S3 storage.")

            return S3Manager(access_key, secret_key)
        else:
            raise ValueError("Invalid storage type specified.")

```

## StorageBase.py

```python
from abc import ABC, abstractmethod
from mimetypes import guess_type
from typing import List, Dict, Any


class StorageBase(ABC):
    """
    An abstract base class for storage management.

    This class defines the interface for various storage types such as local
    file storage and cloud storage (e.g., AWS S3). Concrete implementations must
    provide the actual methods for handling file operations.
    """

    @abstractmethod
    def save_file(self, content: str, file_path: str, overwrite: bool = False) -> None:
        """
        Save content to a specified file.

        :param content: The content to save to the file.
        :param file_path: The destination file path, including the folder structure.
        :param overwrite: A flag indicating whether to overwrite an existing file.
        :raises Exception: If there is an error during the save operation.
        """
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """
        Read content from a specified file.

        :param file_path: The path of the file to read.
        :return: The content of the file.
        :raises Exception: If there is an error during the read operation.
        """
        pass

    def save_yaml(self, yaml_path: str, data: Dict[Any, Any]) -> None:
        """
        Save a dictionary as a YAML file.

        :param yaml_path: The path where the YAML file will be saved.
        :param data: The dictionary to save as YAML.
        """
        # This can be overridden by subclasses if needed
        pass

    def load_yaml(self, yaml_path: str) -> Dict:
        """
        Load data from a YAML file into a dictionary.

        :param yaml_path: The path of the YAML file to load.
        :return: A dictionary containing the loaded data.
        """
        # This can be overridden by subclasses if needed
        return {}

    @abstractmethod
    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Move a file from one path to another.

        :param current_path: The current file path.
        :param new_path: The target path to which the file should be moved.
        :raises Exception: If there is an error during the move operation.
        """
        pass

    @abstractmethod
    def list_staged_files(self) -> List[str]:
        """
        List all files in the current storage context.

        :return: A list of file paths.
        :raises Exception: If there is an error while listing files.
        """
        pass

    @abstractmethod
    def write_to_csv(self, file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Write a list of dictionaries to a CSV file.

        :param file_name: The name of the CSV file to create or append to.
        :param dictionaries: The list of dictionaries to write.
        :param fieldnames: The order of the fields in the CSV.
        :raises Exception: If there is an error during the write operation.
        """
        pass

    @abstractmethod
    def write_to_yaml(self, data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        """
        Write data to a YAML file.

        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Flag indicating whether to overwrite existing files.
        :raises Exception: If there is an error during the write operation.
        """
        pass

    def add_new_user_file_folder(self, user_id: str) -> None:
        """
        Create a new folder for user file storage.

        Subclasses can implement this as needed.

        :param user_id: The identifier for the user for whom the folder is created.
        """
        pass

    @staticmethod
    def is_image_file(full_address: str) -> bool:
        """
        Check if a file is an image.

        :param full_address: The path to the file.
        :return: True if the file is an image, False otherwise.
        """
        mime_type, _ = guess_type(full_address)
        return mime_type is not None and mime_type.startswith('image')

```

## S3Manager.py

```python
import logging
import os
from typing import List, Dict, Any
import boto3
import yaml
from botocore.exceptions import ClientError
from Data.Files.StorageBase import StorageBase
from Utilities.Constants import DEFAULT_ENCODING
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

    @return_for_error(False, debug_logging=True)
    def save_file(self, content: str, file_path: str = None, overwrite: bool = False) -> bool:
        """
        Save a file to an S3 bucket.

        :param content: The content to be formatted and saved.
        :param file_path: S3 object name including folder prefix.
        :param overwrite: If True, allows overwriting existing files.
        :return: True if file was uploaded, else False.
        """
        # Prevent overwriting without an explicit overwrite
        if not overwrite and self.check_file_exists(file_path):
            logging.warning(f"File {file_path} already exists. Not overwriting.")
            return False

        # Upload the file to the S3 bucket
        try:
            self.s3_client.put_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
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
                return f"[CANNOT READ IMAGE FILE: {full_address}]"

            response = self.s3_client.get_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
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
        
        try:
            self.s3_client.put_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
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
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
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
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                CopySource={'Bucket': os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                             'Key': self.convert_to_s3_path(current_path)},
                Key=self.convert_to_s3_path(new_path)
            )
            self.s3_client.delete_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                Key=self.convert_to_s3_path(current_path)
            )
            logging.info(f"File {current_path} moved to {new_path}.")
        except ClientError as e:
            logging.error(f"FAILED TO MOVE {current_path} TO {new_path}: {e}")

    def list_staged_files(self) -> List[str]:
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
        """
        Writes or appends a list of dictionaries to a CSV file. (NOT IMPLEMENTED)

        :param file_name: The name of the CSV file to save to.
        :param dictionaries: The list of dictionaries to write.
        :param fieldnames: The order of the fields in the CSV.
        """
        logging.error("NOT IMPLEMENTED")

    def write_to_yaml(self, data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        """
        Writes data to a YAML file in S3. (NOT IMPLEMENTED)

        :param data: The data to write to the YAML file.
        :param yaml_path: The path where the YAML file will be saved.
        :param overwrite: Determines if the YAML file should be replaced or appended to.
        """
        logging.error("NOT IMPLEMENTED")

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

    def check_file_exists(self, file_key: str) -> bool:
        """
        Check if a specific file exists in the S3 bucket.

        :param file_key: The key of the file to check for.
        :return: True if the file exists, False otherwise.
        """
        try:
            self.s3_client.head_object(
                Bucket=os.getenv("THE-THINKER-S3-STANDARD-BUCKET-ID"),
                Key=self.convert_to_s3_path(file_key)
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logging.error(f"Error checking if file exists: {e}")
                raise

    def add_new_user_file_folder(self, user_id: str) -> None:
        """
        Add a new user file folder. (Not necessary in S3, as folders are virtual.)

        :param user_id: The ID of the user for which to create a folder.
        """
        pass  # S3 does not require explicit folder creation.

    @staticmethod
    def convert_to_s3_path(path: str) -> str:
        """
        Converts a file system path to an Amazon S3-compatible path.

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

```

## FileManagement.py

```python
import csv
import logging
import os
import shutil
import sys
from typing import List, Dict, Any
import yaml
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
    prompt injection and extraction of data from unauthorized areas.
    ONLY information within the 'FileData' directory can be edited by the user.

    ToDo: (Bug) tries to create a category folder even when set to S3?
    """

    # Directories for file and configuration data
    file_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/FileData')
    config_data_directory = os.path.join(os.path.dirname(__file__), '../../../UserData/UserConfigs')

    def __init__(self):
        ErrorHandler.setup_logging()

    @staticmethod
    @handle_errors(raise_errors=True)
    def save_file(content: str, file_path: str, overwrite: bool = False) -> None:
        """
        Saves the response content to a specified file.

        :param content: The content to be formatted and saved
        :param file_path: The file name with extension, prefixed by category folder id
        :param overwrite: Whether the file should be overwritten
        :raises Exception: If the content exceeds the maximum file size
        """
        if sys.getsizeof(content) > MAX_FILE_SIZE:
            raise Exception("File is too large. Maximum size is 10 MB.")

        data_path = os.path.join(FileManagement.file_data_directory, file_path)
        mode = "w" if overwrite or not os.path.exists(data_path) else "a"

        with open(data_path, mode, encoding=DEFAULT_ENCODING) as file:
            file.write(content)
            logging.info(f"File {'overwritten' if overwrite else 'saved'}: {data_path}")

    def read_file(self, full_address: str) -> str:
        """
        Reads the content of a specified file.

        :param full_address: The file name to read, including category folder prefix
        :return: The content of the file or an error message
        """
        full_path = os.path.join(FileManagement.file_data_directory, full_address)
        logging.info(f"Loading file content from: {full_path}")

        if self.is_image_file(full_address):
            logging.warning(f"Attempted to read an image file: {full_address}")
            return f"CANNOT READ IMAGE FILE: {full_address}"

        try:
            with open(full_path, 'r', encoding=DEFAULT_ENCODING) as file:
                return file.read()
        except FileNotFoundError:
            logging.exception(f"File not found: {full_address}")
            return f"FILE NOT FOUND: {full_address}"
        except Exception:
            logging.exception("An unexpected error occurred.")
            return f"FAILED TO LOAD: {full_address}"

    def move_file(self, current_path: str, new_path: str) -> None:
        """
        Moves a file within the file storage.

        :param current_path: The current file path
        :param new_path: The new file path
        """
        try:
            staged_file_path = os.path.join(FileManagement.file_data_directory, current_path)
            new_file_path = os.path.join(FileManagement.file_data_directory, new_path)
            shutil.move(staged_file_path, new_file_path)
            logging.info(f"{current_path} moved to {new_path}")
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
    def load_yaml(yaml_path: str) -> Dict[str, Any]:
        """
        Loads existing data from a YAML file if available.

        :param yaml_path: The path to the YAML file.
        :return: A dictionary containing the loaded data or an empty dictionary.
        """
        existing_data = {}
        full_path = os.path.join(FileManagement.config_data_directory, yaml_path)

        if os.path.isfile(full_path) and os.path.getsize(full_path) > 0:
            try:
                with open(full_path, 'r', encoding=DEFAULT_ENCODING) as yaml_file:
                    existing_data = yaml.safe_load(yaml_file) or {}
                logging.info(f"YAML data loaded from: {full_path}")
            except (FileNotFoundError, yaml.YAMLError) as e:
                logging.error(f"Error reading YAML file: {e}")
        else:
            logging.info(f"No existing data file found at: {full_path}")

        return existing_data

    @staticmethod
    def list_staged_files() -> List[str]:
        """
        Lists all files in the user's staging directory.

        :return: A list of staged file paths that belong to the user's staging directory
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
        """
        Returns a string where each line is prepended with its line number.

        :param lines: A list of strings.
        :return: A concatenated string with line numbers.
        """
        return ''.join([f"{i + 1}: {line}" for i, line in enumerate(lines)])

    @staticmethod
    def write_to_csv(file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        """
        Writes or appends a list of dictionaries to a CSV file.

        :param file_name: The name of the CSV file to save to.
        :param dictionaries: The list of dictionaries to write.
        :param fieldnames: The order of the fields in the CSV.
        """
        logging.info(f"Data being written to CSV: {dictionaries}")
        file_path = os.path.join(os.path.dirname(__file__), '../../UserData/DataStores', file_name)
        file_exists = os.path.isfile(file_path) and os.path.getsize(file_path) > 0
        mode = 'a' if file_exists else 'w'

        with open(file_path, mode=mode, newline='', encoding=DEFAULT_ENCODING) as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists:
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
        :param overwrite: Determines if the YAML file should be replaced or appended to.
        """
        mode = "w" if overwrite or not os.path.exists(yaml_path) else "a"
        
        with open(yaml_path, mode, encoding=DEFAULT_ENCODING) as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False, Dumper=MyDumper, allow_unicode=True)

    @staticmethod
    def regex_refactor(target_string: str, replacement: str, file_path: str) -> None:
        """
        Replaces every instance of the target with the replacement string in a file.

        :param target_string: The text to be replaced.
        :param replacement: The text to replace the target string.
        :param file_path: The file path including category prefix.
        :raises ValueError: If the rewrite operation fails.
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
        Creates a new file staging folder for a new user.

        :param user_id: The unique identifier for the user for which the folder will be created.
        """
        new_directory = os.path.join(FileManagement.file_data_directory, str(user_id))
        os.makedirs(new_directory, exist_ok=True)


if __name__ == '__main__':
    try:
        numbered_lines = FileManagement().read_file("test/Writing.py")
        print(numbered_lines)
    except Exception as e:
        logging.exception(f"An error occurred: {e}")

```


