import os

import yaml


class Configuration:

    persona_specification_path = os.path.join(os.path.dirname(__file__), '..', 'Personas', 'PersonaSpecification')

    @staticmethod
    def load_config(yaml_file="Config.yaml"):
        """Loads the configuration from a YAML file and extracts values.

        :param yaml_file: The path to the YAML file.
        :returns dict: A dictionary containing the extracted configuration values.
        """
        config_path = os.path.join(Configuration.persona_specification_path, yaml_file)
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config


if __name__ == '__main__':
    # Example usage
    config = Configuration()
    config_items = config.load_config()
    print(config_items['documentation']['style'])  # Output: reStructuredText
    print(config_items['writing'])
