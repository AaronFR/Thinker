import logging
import os

from typing import Mapping

from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context

USER_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'UserConfigs')


class Configuration:

    @staticmethod
    def deep_merge(dict1, dict2):
        """
        Deeply merges dict2 into dict1. dict2 takes precedence over dict1.

        :param dict1: The base dictionary.
        :param dict2: The dictionary to merge over `dict1`.
        :returns: The merged dictionary.
        """
        for key, value in dict2.items():
            if isinstance(value, Mapping) and key in dict1 and isinstance(dict1[key], Mapping):
                Configuration.deep_merge(dict1[key], value)
            else:
                dict1[key] = value
        return dict1

    @staticmethod
    def load_config(yaml_file="Config.yaml"):
        """
        Loads the configuration from the baseline YAML file then merging the users config on top
        extracting the combined values.

        :param yaml_file: The path to the YAML file
        :returns dict: A dictionary containing the extracted configuration values
        """
        config = StorageMethodology.select().load_yaml(yaml_file)
        user_config = StorageMethodology.select().load_yaml(f"{get_user_context()}.yaml")

        # Merge user_config into config
        merged_config = Configuration.deep_merge(config, user_config)

        return merged_config

    @staticmethod
    def update_config_field(field_path, value):
        """
        Updates a particular field in the users YAML configuration file.
        For first time changes, a new user config file will be created automatically

        :param field_path: The dot-separated path to the field to update (e.g., 'interface.dark_mode')
        :param value: The value to set for the specified field
        :returns: None
        """
        file_storage = StorageMethodology.select()
        user_config_path = os.path.join(get_user_context() + ".yaml")

        config = file_storage.load_yaml(user_config_path)

        # Navigate to the specified field and update the value
        keys = field_path.split('.')
        current = config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

        # Save the updated configuration back to the YAML file
        file_storage.save_yaml(user_config_path, config)


if __name__ == '__main__':
    # Example usage
    config = Configuration()
    config_items = config.load_config()
    print(config_items)
    print(config_items['documentation']['style'])  # Output: reStructuredText
    print(config_items['writing'])
