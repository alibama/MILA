import yaml
import os

def load_config(config_path="config.yaml"):
    """
    Load configuration from the YAML file.
    
    Args:
        config_path (str): Path to the configuration YAML file.
        
    Returns:
        dict: Loaded configuration as a dictionary.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)
    
    return config