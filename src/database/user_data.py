import json
import os
import logging
from datetime import datetime

class UserData:
    """
    A simple user data storage and retrieval system.
    """
    
    def __init__(self, storage_file="user_data.json"):
        """
        Initialize the user data storage.
        
        Args:
            storage_file (str): Path to the storage file
        """
        self.storage_file = storage_file
        self.data = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_file) if os.path.dirname(self.storage_file) else '.', exist_ok=True)
        
        # Load existing data
        self._load_data()
        logging.info(f"UserData initialized with storage file: {self.storage_file}")

    def _load_data(self):
        """
        Loads data from the storage file.
        """
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                logging.error(f"Error loading user data: {e}")
                self.data = {}
        else:
            self.data = {}

    def _save_data(self):
        """
        Saves data to the storage file.
        """
        try:
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving user data: {e}")

    def add_user(self, user_id, user_info):
        """
        Adds a new user to the data storage.
        
        Args:
            user_id (str): Unique identifier for the user
            user_info (dict): User information dictionary
            
        Returns:
            bool: Success status
        """
        if not user_id or not user_info:
            return False
            
        self.data[user_id] = user_info
        self.data[user_id]["created_at"] = datetime.now().isoformat()
        self._save_data()
        logging.info(f"User {user_id} added.")
        return True

    def get_user(self, user_id):
        """
        Retrieves user information.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: User information or None if not found
        """
        return self.data.get(user_id)

    def update_user(self, user_id, updated_info):
        """
        Updates user information.
        
        Args:
            user_id (str): Unique identifier for the user
            updated_info (dict): Updated user information
            
        Returns:
            bool: Success status
        """
        if not user_id or not updated_info:
            return False
            
        if user_id in self.data:
            self.data[user_id].update(updated_info)
            self.data[user_id]["updated_at"] = datetime.now().isoformat()
            self._save_data()
            logging.info(f"User {user_id} updated.")
            return True
        else:
            logging.warning(f"User {user_id} not found.")
            return False

    def delete_user(self, user_id):
        """
        Deletes a user from storage.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            bool: Success status
        """
        if not user_id:
            return False
            
        if user_id in self.data:
            del self.data[user_id]
            self._save_data()
            logging.info(f"User {user_id} deleted.")
            return True
        else:
            logging.warning(f"User {user_id} not found.")
            return False
    
    def store_user_query(self, user_id, query, response):
        """
        Store a user query and AI response.
        
        Args:
            user_id (str): User identifier
            query (str): User query
            response (str): AI response
            
        Returns:
            bool: Success status
        """
        if not user_id or not query:
            return False
            
        # Create user if not exists
        if user_id not in self.data:
            self.data[user_id] = {
                "created_at": datetime.now().isoformat(),
                "interactions": []
            }
        
        # Add interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response
        }
        
        if "interactions" not in self.data[user_id]:
            self.data[user_id]["interactions"] = []
            
        self.data[user_id]["interactions"].append(interaction)
        self._save_data()
        
        return True
    
    def get_user_history(self, user_id, limit=10):
        """
        Get user interaction history.
        
        Args:
            user_id (str): User identifier
            limit (int): Maximum number of interactions to return
            
        Returns:
            list: List of interactions