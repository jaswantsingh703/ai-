import os
import yaml
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Centralized configuration class for the AI Assistant project.
    Loads from config.yaml and .env files.
    """
    
    # Default configuration
    _config = {
        # General Settings
        "project_name": "AI Assistant",
        "version": "1.0.0",
        "debug_mode": True,
        
        # Paths
        "base_dir": os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data_dir": "data",
        "logs_dir": "logs",
        "models_dir": "models",
        
        # Model Configuration
        "default_model_type": "gpt4all",
        "default_model_path": "models/gpt4all-j-v1.3-groovy.bin",
        "fallback_model_type": "gpt4all",
        
        # API Keys (will be overridden by environment variables if present)
        "openai_api_key": "",
        "huggingface_api_key": "",
        "google_search_api_key": "",
        "google_search_engine_id": "",
        
        # Logging Settings
        "logging_level": "INFO",
        
        # Security Settings
        "enable_system_control": False,  # Disable potentially dangerous system control by default
        "allowed_commands": ["ls", "dir", "echo", "pwd", "whoami", "date", "time"],
        
        # GUI Settings
        "gui_theme": "light",
        "gui_font_size": 12
    }
    
    @classmethod
    def load(cls, config_file="config.yaml"):
        """
        Load configuration from a YAML file.
        """
        config_path = os.path.join(cls._config["base_dir"], config_file)
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as file:
                    loaded_config = yaml.safe_load(file)
                    if loaded_config:
                        cls._config.update(loaded_config)
                logging.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logging.error(f"Error loading configuration: {e}")
        else:
            logging.warning(f"Configuration file not found: {config_path}")
            
        # Override with environment variables (env vars take precedence)
        cls._load_from_env()
        
        # Ensure absolute paths for directories
        for dir_key in ["data_dir", "logs_dir", "models_dir"]:
            if not os.path.isabs(cls._config[dir_key]):
                cls._config[dir_key] = os.path.join(cls._config["base_dir"], cls._config[dir_key])
        
        # Initialize directories
        cls.init_directories()
        
        return cls
    
    @classmethod
    def _load_from_env(cls):
        """
        Load configuration from environment variables.
        """
        # Map environment variables to config keys
        env_mapping = {
            "OPENAI_API_KEY": "openai_api_key",
            "HUGGINGFACE_API_KEY": "huggingface_api_key",
            "GOOGLE_SEARCH_API_KEY": "google_search_api_key",
            "GOOGLE_SEARCH_ENGINE_ID": "google_search_engine_id",
            "DEBUG_MODE": "debug_mode",
            "LOGGING_LEVEL": "logging_level",
            "DEFAULT_MODEL_TYPE": "default_model_type",
            "ENABLE_SYSTEM_CONTROL": "enable_system_control"
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                # Convert string boolean values to actual booleans
                if os.environ[env_var].lower() in ["true", "false"]:
                    cls._config[config_key] = os.environ[env_var].lower() == "true"
                else:
                    cls._config[config_key] = os.environ[env_var]
    
    @classmethod
    def get(cls, key, default=None):
        """
        Get a configuration value.
        """
        return cls._config.get(key, default)
    
    @classmethod
    def set(cls, key, value):
        """
        Set a configuration value.
        """
        cls._config[key] = value
    
    @classmethod
    def init_directories(cls):
        """
        Creates necessary directories if they do not exist.
        """
        for directory in [cls._config["data_dir"], cls._config["logs_dir"], cls._config["models_dir"]]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logging.info(f"Created directory: {directory}")