import os
import json
import logging
from datetime import datetime

def setup_logging(log_file="logs/app.log"):
    """
    Sets up logging configuration.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Logging initialized.")

def read_json(file_path):
    """
    Reads a JSON file and returns the data.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None
    
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def write_json(file_path, data):
    """
    Writes data to a JSON file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    logging.info(f"Data written to {file_path}")

def get_current_timestamp():
    """
    Returns the current timestamp as a string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_directory_exists(directory):
    """
    Ensures the specified directory exists, creating it if necessary.
    """
    os.makedirs(directory, exist_ok=True)
    logging.info(f"Ensured directory exists: {directory}")

# Example Usage
if __name__ == "__main__":
    setup_logging()
    print(get_current_timestamp())
    ensure_directory_exists("data")
    write_json("data/sample.json", {"message": "Hello, World!"})
    print(read_json("data/sample.json"))
