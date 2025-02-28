# src/utils/model_manager.py

import os
import logging
import requests
import hashlib
from tqdm import tqdm
from src.utils.config import Config

class ModelManager:
    """
    Manages downloading and verification of AI models.
    """
    
    def __init__(self):
        """Initialize the model manager."""
        self.models_dir = Config.get("models_dir", "models")
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Model information (name, url, expected file size, md5 hash)
        self.models = {
            "gpt4all": {
                "filename": "gpt4all-j-v1.3-groovy.bin",
                "url": "https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin",
                "size": 3785248283,
                "md5": "81a09a0ddf89f7b8a2a5e7f42ad24097"
            },
            "whisper-base": {
                "filename": "whisper-base.pt",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
                "size": 461262023,
                "md5": "e9d5ff33887d4838dc57b7e1a643031d"
            },
            "whisper-medium": {
                "filename": "whisper-medium.pt",
                "url": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
                "size": 1421805354,
                "md5": "5e5c08ff0206907a0878a452de481596"
            },
            "llama-7b": {
                "filename": "llama-7b.ggmlv3.q4_0.bin",
                "url": "", # Requires Meta access
                "size": 4073259968,
                "md5": ""
            }
        }
        
    def check_model(self, model_name):
        """
        Check if a model exists and is valid.
        
        Args:
            model_name (str): Name of the model to check
            
        Returns:
            bool: True if model exists and is valid, False otherwise
        """
        if model_name not in self.models:
            logging.error(f"Unknown model: {model_name}")
            return False
            
        model_info = self.models[model_name]
        model_path = os.path.join(self.models_dir, model_info["filename"])
        
        # Check if file exists
        if not os.path.exists(model_path):
            logging.warning(f"Model file not found: {model_path}")
            return False
            
        # Check file size (optional quick check)
        if model_info["size"] > 0:  # Only check if we know the size
            file_size = os.path.getsize(model_path)
            if file_size < model_info["size"] * 0.9 or file_size > model_info["size"] * 1.1:
                logging.warning(f"Model file size mismatch for {model_name}: expected ~{model_info['size']}, got {file_size}")
                return False
            
        # Check MD5 hash (if provided)
        if model_info["md5"]:
            file_hash = self._get_file_hash(model_path)
            if file_hash != model_info["md5"]:
                logging.warning(f"Model file hash mismatch for {model_name}: expected {model_info['md5']}, got {file_hash}")
                return False
            
        return True
    
    def _get_file_hash(self, file_path):
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: MD5 hash
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def download_model(self, model_name):
        """
        Download a model if it doesn't exist or is invalid.
        
        Args:
            model_name (str): Name of the model to download
            
        Returns:
            bool: True if download successful, False otherwise
        """
        if model_name not in self.models:
            logging.error(f"Unknown model: {model_name}")
            return False
            
        if self.check_model(model_name):
            logging.info(f"Model {model_name} already exists and is valid.")
            return True
            
        model_info = self.models[model_name]
        model_path = os.path.join(self.models_dir, model_info["filename"])
        
        # Skip for models requiring special access (like Llama)
        if not model_info["url"]:
            logging.warning(f"Model {model_name} requires manual download. Please download and place in {model_path}")
            return False
            
        logging.info(f"Downloading model {model_name} from {model_info['url']}")
        
        try:
            # Stream download with progress bar
            response = requests.get(model_info["url"], stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f, tqdm(
                desc=model_info["filename"],
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            # Verify download
            if self.check_model(model_name):
                logging.info(f"Model {model_name} downloaded successfully.")
                return True
            else:
                logging.error(f"Downloaded model {model_name} failed validation.")
                return False
                
        except Exception as e:
            logging.error(f"Error downloading model {model_name}: {e}")
            return False
    
    def get_model_path(self, model_name):
        """
        Get the path to a model file, downloading if necessary.
        
        Args:
            model_name (str): Name of the model
            
        Returns:
            str: Path to the model file or None if unavailable
        """
        if model_name not in self.models:
            logging.error(f"Unknown model: {model_name}")
            return None
            
        model_info = self.models[model_name]
        model_path = os.path.join(self.models_dir, model_info["filename"])
        
        if not self.check_model(model_name):
            if not self.download_model(model_name):
                return None
                
        return model_path
    
    def list_available_models(self):
        """
        List all available models and their status.
        
        Returns:
            dict: Model status information
        """
        model_status = {}
        
        for model_name in self.models:
            model_info = self.models[model_name]
            model_path = os.path.join(self.models_dir, model_info["filename"])
            
            status = {
                "name": model_name,
                "filename": model_info["filename"],
                "path": model_path,
                "available": os.path.exists(model_path),
                "size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2) if os.path.exists(model_path) else 0,
                "expected_size_mb": round(model_info["size"] / (1024 * 1024), 2) if model_info["size"] else "Unknown",
                "valid": self.check_model(model_name)
            }
            
            model_status[model_name] = status
            
        return model_status