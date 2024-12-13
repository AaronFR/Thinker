# storage_base.py
from abc import ABC, abstractmethod
from mimetypes import guess_type
from typing import List, Dict


class StorageBase:
    @abstractmethod
    def save_file(self, content: str, file_path: str, overwrite: bool = False) -> None:
        pass

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        pass

    @abstractmethod
    def move_file(self, current_path: str, new_path: str):
        pass

    @abstractmethod
    def list_staged_files(self) -> List[str]:
        pass

    # @abstractmethod
    # def delete_file(self, file_path: str) -> None:
    #     pass

    @abstractmethod
    def write_to_csv(self, file_name: str, dictionaries: List[Dict], fieldnames: List[str]) -> None:
        pass

    @abstractmethod
    def write_to_yaml(self, data: Dict[str, object], yaml_path: str, overwrite: bool = False) -> None:
        pass

    def add_new_user_file_folder(self, user_id):
        pass

    # Shared functions

    @staticmethod
    def is_image_file(full_address: str) -> bool:
        """Utility method to check if the file is an image."""
        mime_type, _ = guess_type(full_address)
        return mime_type is not None and mime_type.startswith('image')