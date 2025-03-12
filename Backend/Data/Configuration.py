import os
from typing import Mapping, Dict, Any

from Data.Files.StorageMethodology import StorageMethodology
from Utilities.Contexts import get_user_context, get_user_configuration, set_user_configuration
from Utilities.Decorators.Decorators import handle_errors


class Configuration:
    """
    Configuration class to manage loading and updating configuration settings
    from YAML and CSV files. This includes support for deep merging of
    configurations and handling user-specific settings.
    """

    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
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
    @handle_errors
    def load_config(yaml_file="Config.yaml"):
        """
        Loads the configuration from the baseline YAML file then merges the user's config on top,
        extracting the combined values.

        :param yaml_file: The path to the YAML file
        :returns: A dictionary containing the extracted configuration values
        :raises FileNotFoundError: If the specified YAML file does not exist.
        """
        full_config = get_user_configuration()
        if not full_config:
            default_config = StorageMethodology.select().load_yaml(yaml_file)
            user_config = StorageMethodology.select().load_yaml(f"{get_user_context()}.yaml")

            # Merge user_config into config
            full_config = Configuration.deep_merge(default_config, user_config)

            set_user_configuration(full_config)

        return full_config

    @staticmethod
    def update_config_field(field_path: str, value: Any) -> None:
        """
        Updates a particular field in the user's YAML configuration file.
        For first-time changes, a new user config file will be created automatically.

        :param field_path: The dot-separated path to the field to update (e.g., 'interface.dark_mode').
        :param value: The value to set for the specified field.
        :raises FileNotFoundError: If the user configuration file does not exist.
        :raises Exception: If there are issues while saving the configuration.
        """
        file_storage = StorageMethodology.select()
        user_config_path = os.path.join(get_user_context() + ".yaml")

        user_config = file_storage.load_yaml(user_config_path)

        # Navigate to the specified field and update the value
        keys = field_path.split('.')
        current = user_config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

        # Save the updated configuration back to the YAML file
        file_storage.save_yaml(user_config_path, user_config)


if __name__ == '__main__':
    # Example usage
    config = Configuration()
    config_items = config.load_config()
    print(config_items)
    print(config_items['system_messages']['categorisation_message'])
