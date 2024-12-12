import os

from Data.FileManagement import FileManagement
from Data.S3Manager import S3Manager
from Data.StorageBase import StorageBase


class StorageMethodology:
    """
    A factory class to create different storage managers based on the storage type.
    ToDo: Add a check that access_keys are defined for a class singleton initialisation, i.e. once during deployment
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
            return S3Manager(
                os.getenv("THE-THINKER-S3-STANDARD-ACCESS-KEY"),
                os.getenv("THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY")
            )
        else:
            raise ValueError("Invalid storage type specified.")
