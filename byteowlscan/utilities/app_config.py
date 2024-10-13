# my_library/utilities/app_config.py
import yaml

class AppConfig:
    config = None
    
    def init_config(file_path):
        AppConfig.config = AppConfig.load_config(file_path)

    @staticmethod
    def load_config(file_path):
        """Load YAML configuration file."""
        try:
            with open(file_path, 'r') as file:
                config = yaml.safe_load(file)
                return config
        except FileNotFoundError:
            print(f"Configuration file '{file_path}' not found.")
            return None
        except yaml.YAMLError as exc:
            print(f"Error parsing YAML file: {exc}")
            return None

    @staticmethod
    def get(key, default=None):
        return AppConfig.config.get(key, default)
    