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

