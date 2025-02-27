import json
import os
import logging

class UserData:
    """
    A simple user data storage and retrieval system.
    """
    
    def __init__(self, storage_file="user_data.json"):
        self.storage_file = storage_file
        self._load_data()
        logging.info("UserData initialized with storage file: " + self.storage_file)

    def _load_data(self):
        """
        Loads data from the storage file.
        """
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save_data(self):
        """
        Saves data to the storage file.
        """
        with open(self.storage_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def add_user(self, user_id, user_info):
        """
        Adds a new user to the data storage.
        :param user_id: Unique identifier for the user.
        :param user_info: Dictionary containing user details.
        """
        self.data[user_id] = user_info
        self._save_data()
        logging.info(f"User {user_id} added.")

    def get_user(self, user_id):
        """
        Retrieves user information.
        :param user_id: Unique identifier for the user.
        """
        return self.data.get(user_id, None)

    def update_user(self, user_id, updated_info):
        """
        Updates user information.
        :param user_id: Unique identifier for the user.
        :param updated_info: Dictionary containing updated user details.
        """
        if user_id in self.data:
            self.data[user_id].update(updated_info)
            self._save_data()
            logging.info(f"User {user_id} updated.")
        else:
            logging.warning(f"User {user_id} not found.")

    def delete_user(self, user_id):
        """
        Deletes a user from storage.
        :param user_id: Unique identifier for the user.
        """
        if user_id in self.data:
            del self.data[user_id]
            self._save_data()
            logging.info(f"User {user_id} deleted.")
        else:
            logging.warning(f"User {user_id} not found.")

# Example Usage
if __name__ == "__main__":
    user_db = UserData()
    user_db.add_user("user1", {"name": "John Doe", "email": "johndoe@example.com"})
    print(user_db.get_user("user1"))
    user_db.update_user("user1", {"email": "john.doe@newdomain.com"})
    print(user_db.get_user("user1"))
    user_db.delete_user("user1")
    print(user_db.get_user("user1"))
