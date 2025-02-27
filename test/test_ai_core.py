import unittest
from src.ai_core.model_integration import AIModel

class TestAICore(unittest.TestCase):
    """
    Unit tests for AI core functionalities.
    """
    
    def setUp(self):
        """
        Setup before each test.
        """
        self.ai_model = AIModel(model_type="gpt-3.5", model_path="models/gpt_model.bin")
    
    def test_generate_response(self):
        """
        Test if AI model generates a response.
        """
        input_text = "What is AI?"
        response = self.ai_model.generate_response(input_text)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "Response should not be empty")
    
    def test_generate_response_invalid_input(self):
        """
        Test how AI model handles empty input.
        """
        response = self.ai_model.generate_response("")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0, "Response should provide an informative message")

if __name__ == "__main__":
    unittest.main()
