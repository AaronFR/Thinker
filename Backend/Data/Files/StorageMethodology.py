import os

from Constants.Constants import THE_THINKER_S3_STANDARD_ACCESS_KEY, THE_THINKER_S3_STANDARD_SECRET_ACCESS_KEY, \
    STORAGE_TYPE, LOCAL_STORAGE, AWS_S3_STORAGE
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
        storage_type = os.getenv(STORAGE_TYPE, LOCAL_STORAGE)

        if storage_type == LOCAL_STORAGE:
            return FileManagement()
        elif storage_type == AWS_S3_STORAGE:
            access_key = os.getenv(THE_THINKER_S3_STANDARD_ACCESS_KEY)
            secret_key = os.getenv(THE_THINKER_S3_STANDARD_SECRET_ACCESS_KEY)

            if not access_key or not secret_key:
                raise ValueError("AWS access keys must be defined for S3 storage.")

            return S3Manager(access_key, secret_key)
        else:
            raise ValueError(f"Invalid storage type specified: {storage_type}")

    @staticmethod
    def extract_file_name(file_reference: str) -> str:
        """Extracts the file name from a given file path or S3 reference.

        :param file_reference: The file path or S3 reference as a string.
        :return: The extracted file name.
        """
        file_name = file_reference.split("/")[-1] if "/" in file_reference else file_reference.split("\\")[-1]
        return file_name
