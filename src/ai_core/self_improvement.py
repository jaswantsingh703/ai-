import logging
import os

class SelfImprovement:
    def __init__(self, storage_path="generated_tools/"):
        """
        Initialize AI Self-Improvement module.
        """
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        logging.info("Self-Improvement module initialized.")

    def generate_code(self, description):
        """
        Generate Python script based on description.
        """
        base_script = f"""# Auto-generated script for: {description}\n\ndef main():\n    print(\"Hello from AI-generated script!\")\n\nif __name__ == \"__main__\":\n    main()\n"""
        return base_script

    def save_generated_code(self, filename, code):
        """
        Save generated code to a file.
        """
        file_path = os.path.join(self.storage_path, filename)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            logging.info(f"Generated tool saved: {file_path}")
            return file_path
        except Exception as e:
            logging.error(f"Error saving generated code: {e}")
            return None

# Example Usage
if __name__ == "__main__":
    self_improve = SelfImprovement()
    code = self_improve.generate_code("Simple AI Task Automation")
    saved_file = self_improve.save_generated_code("ai_generated_tool.py", code)
    if saved_file:
        print("Generated tool saved at:", saved_file)
