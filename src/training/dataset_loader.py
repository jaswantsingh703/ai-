import os
import logging
import pandas as pd
from datasets import load_dataset

class DatasetLoader:
    """
    A class to load and preprocess datasets for training AI models.
    """
    
    def __init__(self, dataset_name="wikitext", data_dir="data"):
        self.dataset_name = dataset_name
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        logging.info(f"DatasetLoader initialized for dataset: {self.dataset_name}")

    def load_huggingface_dataset(self, split="train"):
        """
        Loads dataset from Hugging Face datasets.
        :param split: Dataset split (train, test, validation)
        :return: Loaded dataset
        """
        logging.info(f"Loading Hugging Face dataset: {self.dataset_name} ({split})")
        dataset = load_dataset(self.dataset_name, split=split)
        return dataset

    def load_csv_dataset(self, file_path):
        """
        Loads a CSV file as a pandas DataFrame.
        :param file_path: Path to the CSV file.
        :return: pandas DataFrame
        """
        if not os.path.exists(file_path):
            logging.error(f"CSV file not found: {file_path}")
            return None
        
        logging.info(f"Loading CSV dataset: {file_path}")
        df = pd.read_csv(file_path)
        return df

    def save_dataset(self, dataset, file_name="dataset.csv"):
        """
        Saves a dataset to a CSV file.
        :param dataset: Dataset to save.
        :param file_name: Name of the output CSV file.
        """
        file_path = os.path.join(self.data_dir, file_name)
        dataset.to_csv(file_path, index=False)
        logging.info(f"Dataset saved to {file_path}")

# Example Usage
if __name__ == "__main__":
    loader = DatasetLoader()
    dataset = loader.load_huggingface_dataset()
    print(dataset)
    
    csv_dataset = loader.load_csv_dataset("data/sample.csv")
    if csv_dataset is not None:
        print(csv_dataset.head())
