import os

class Config:
    """
    Configuration class to store global settings for the AI project.
    """
    
    # General Settings
    PROJECT_NAME = "AI Assistant"
    VERSION = "1.0.0"
    DEBUG_MODE = True
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # Model Configuration
    DEFAULT_MODEL_NAME = "gpt-3.5"
    DEFAULT_TRAINING_EPOCHS = 5
    DEFAULT_BATCH_SIZE = 16
    
    # API Keys & Authentication
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_default_api_key")
    HUGGINGFACE_API_KEY = os.getenv("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", "your_default_huggingface_api_key")
    
    # Logging Settings
    LOGGING_LEVEL = "INFO"
    
    @classmethod
    def init_directories(cls):
        """Creates necessary directories if they do not exist."""
        for directory in [cls.DATA_DIR, cls.LOGS_DIR, cls.MODELS_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

# Initialize directories on import
Config.init_directories()
