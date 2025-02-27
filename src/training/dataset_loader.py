import os
import logging
import pandas as pd
from src.utils.config import Config

# Check if datasets is available
try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    logging.warning("datasets module not available. Hugging Face dataset loading will be limited.")

class DatasetLoader:
    """
    Data loader for training AI models.
    """
    
    def __init__(self, dataset_name=None, data_dir=None):
        """
        Initialize the dataset loader.
        
        Args:
            dataset_name (str): Name of Hugging Face dataset
            data_dir (str): Directory for data files
        """
        self.dataset_name = dataset_name or "wikitext"
        self.data_dir = data_dir or Config.get("data_dir", "data")
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        logging.info(f"DatasetLoader initialized for dataset: {self.dataset_name}")

    def load_huggingface_dataset(self, split="train"):
        """
        Load a dataset from Hugging Face datasets.
        
        Args:
            split (str): Dataset split (train, test, validation)
            
        Returns:
            object: Loaded dataset or None if unavailable
        """
        if not DATASETS_AVAILABLE:
            logging.error("Cannot load Hugging Face dataset: datasets module not available")
            return None
            
        try:
            logging.info(f"Loading Hugging Face dataset: {self.dataset_name} ({split})")
            dataset = load_dataset(self.dataset_name, split=split)
            return dataset
        except Exception as e:
            logging.error(f"Error loading dataset: {e}")
            return None

    def load_csv_dataset(self, file_path=None):
        """
        Load a dataset from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            DataFrame: Loaded dataset or None if unavailable
        """
        # If file_path is not provided, look in the data directory
        if file_path is None:
            file_path = os.path.join(self.data_dir, "dataset.csv")
            
        if not os.path.exists(file_path):
            logging.error(f"CSV file not found: {file_path}")
            return None
        
        try:
            logging.info(f"Loading CSV dataset: {file_path}")
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logging.error(f"Error loading CSV: {e}")
            return None

    def save_dataset(self, dataset, file_name=None):
        """
        Save a dataset to a CSV file.
        
        Args:
            dataset: Dataset to save (DataFrame or Hugging Face dataset)
            file_name (str): Name of the output file
            
        Returns:
            str: Path to the saved file or None if failed
        """
        if file_name is None:
            file_name = "dataset.csv"
            
        file_path = os.path.join(self.data_dir, file_name)
        
        try:
            # Handle different dataset types
            if isinstance(dataset, pd.DataFrame):
                # Pandas DataFrame
                dataset.to_csv(file_path, index=False)
            elif DATASETS_AVAILABLE and hasattr(dataset, "to_pandas"):
                # Hugging Face dataset
                df = dataset.to_pandas()
                df.to_csv(file_path, index=False)
            else:
                logging.error("Unsupported dataset type")
                return None
                
            logging.info(f"Dataset saved to {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"Error saving dataset: {e}")
            return None

    def preprocess_dataset(self, dataset, text_column="text"):
        """
        Preprocess a dataset for training.
        
        Args:
            dataset: Dataset to preprocess
            text_column (str): Name of the text column
            
        Returns:
            object: Preprocessed dataset
        """
        try:
            # For pandas DataFrame
            if isinstance(dataset, pd.DataFrame):
                # Basic preprocessing: remove null values, strip whitespace
                if text_column in dataset.columns:
                    dataset = dataset.dropna(subset=[text_column])
                    dataset[text_column] = dataset[text_column].str.strip()
                    
            # For Hugging Face dataset
            elif DATASETS_AVAILABLE and hasattr(dataset, "filter"):
                # Remove empty or null examples
                dataset = dataset.filter(lambda example: example[text_column] is not None and len(example[text_column].strip()) > 0)
            
            return dataset
        except Exception as e:
            logging.error(f"Error preprocessing dataset: {e}")
            return dataset  # Return original dataset on error