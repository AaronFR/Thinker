import os
import yaml

from typing import Mapping


class Configuration:
    data_path = os.path.join(os.path.dirname(__file__), 'DataStores')

    @staticmethod
    def deep_merge(dict1, dict2):
        """Deeply merges dict2 into dict1. dict2 takes precedence over dict1."""
        for key, value in dict2.items():
            if isinstance(value, Mapping) and key in dict1 and isinstance(dict1[key], Mapping):
                Configuration.deep_merge(dict1[key], value)
            else:
                dict1[key] = value
        return dict1

    @staticmethod
    def load_config(yaml_file="Config.yaml"):
        """Loads the configuration from a YAML file and extracts values.

        :param yaml_file: The path to the YAML file
        :returns dict: A dictionary containing the extracted configuration values
        """
        config_path = os.path.join(Configuration.data_path, yaml_file)
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        user_config_path = os.path.join(Configuration.data_path, 'UserConfig.yaml')
        with open(user_config_path, 'r') as file:
            user_config = yaml.safe_load(file)

        # Merge user_config into config
        merged_config = Configuration.deep_merge(config, user_config)

        return merged_config

    @staticmethod
    def update_config_field(field_path, value, yaml_file="UserConfig.yaml"):
        """Updates a particular field in the users YAML configuration file.
        For first time changes, the config file will be created automatically

        :param field_path: The dot-separated path to the field to update (e.g., 'interface.dark_mode')
        :param value: The value to set for the specified field
        :param yaml_file: The path to the YAML file
        :returns: None
        """
        config_path = os.path.join(Configuration.data_path, yaml_file)

        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file) or {}
        else:
            config = {}

        # Navigate to the specified field and update the value
        keys = field_path.split('.')
        current = config
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value

        # Save the updated configuration back to the YAML file
        with open(config_path, 'w') as file:
            yaml.safe_dump(config, file)


if __name__ == '__main__':
    # Example usage
    config = Configuration()
    config_items = config.load_config()
    print(config_items['documentation']['style'])  # Output: reStructuredText
    print(config_items['writing'])
