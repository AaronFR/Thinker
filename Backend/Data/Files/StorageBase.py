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
    def list_files(self, category_id: str) -> List[str]:
        """
        List all files that belong to a specified category

        :return: A list of file paths.
        """
        pass

    # @abstractmethod
    # def delete_file(self, file_path: str) -> None:
    #     pass

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

    def add_new_category_folder(self, category_id: str) -> None:
        """
        Create a new category folder.

        This method is not abstract because the implementation can be
        defined in subclasses based on specific storage requirements.

        :param category_id: The ID of the new category folder.
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
