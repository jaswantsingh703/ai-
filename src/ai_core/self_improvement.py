import logging
import os
import time

class SelfImprovement:
    """
    Self-improvement module for generating and storing AI-generated code and tools.
    """
    
    def __init__(self, storage_path="generated_tools/"):
        """
        Initialize the Self-Improvement module.
        
        Args:
            storage_path (str): Path to store generated tools
        """
        self.storage_path = storage_path
        
        # Create storage directory if it doesn't exist
        try:
            if not os.path.exists(self.storage_path):
                os.makedirs(self.storage_path)
            logging.info("Self-Improvement module initialized.")
        except Exception as e:
            logging.error(f"Error initializing Self-Improvement module: {e}")
            # Use current directory as fallback
            self.storage_path = "./"

    def generate_code(self, description):
        """
        Generate Python script based on description.
        
        Args:
            description (str): Description of the desired functionality
            
        Returns:
            str: Generated Python code
        """
        if not description:
            return "# Error: No description provided"
        
        try:
            # This is a simple template - in a real implementation, 
            # you would use an AI model for code generation
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            base_script = f"""# Auto-generated script for: {description}
# Generated on: {timestamp}

def main():
    """\"\"
    Implementation for: {description}
    \"\"\"
    print("Hello from AI-generated script!")
    # TODO: Add implementation for {description}
    
    # Sample implementation
    print("Starting task...")
    # Task-specific code would go here
    print("Task completed.")
    
    return "Task executed successfully"

if __name__ == "__main__":
    result = main()
    print(result)
"""
            return base_script
        except Exception as e:
            logging.error(f"Error generating code: {e}")
            return f"# Error generating code: {str(e)}"

    def save_generated_code(self, filename, code):
        """
        Save generated code to a file.
        
        Args:
            filename (str): Name of the file to save
            code (str): Code content to save
            
        Returns:
            str: Path to the saved file or error message
        """
        if not filename or not code:
            return None
        
        # Ensure filename has .py extension
        if not filename.endswith('.py'):
            filename += '.py'
        
        file_path = os.path.join(self.storage_path, filename)
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            logging.info(f"Generated tool saved: {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"Error saving generated code: {e}")
            return None
    
    def execute_generated_code(self, file_path):
        """
        Execute a generated Python script.
        
        Args:
            file_path (str): Path to the Python script
            
        Returns:
            str: Output of the script execution
        """
        if not os.path.exists(file_path):
            return "Error: File not found."
        
        try:
            # Using exec with isolated namespace
            namespace = {}
            with open(file_path, "r", encoding="utf-8") as f:
                exec(f.read(), namespace)
            
            # Check if main function exists and call it
            if "main" in namespace:
                result = namespace["main"]()
                return f"Script executed successfully. Result: {result}"
            else:
                return "Script executed but no main function found."
        except Exception as e:
            logging.error(f"Error executing generated code: {e}")
            return f"Error executing script: {str(e)}"