import unittest
from src.ai_core.model_integration import AIModel
from src.utils.config import Config

class TestAICore(unittest.TestCase):
    """
    Unit tests for AI core functionalities.
    """
    
    def setUp(self):
        """
        Setup before each test.
        """
        # Use fallback model to avoid network dependencies
        self.ai_model = AIModel(model_type="gpt4all")
    
    def test_model_initialization(self):
        """
        Test if AI model initializes without errors.
        """
        self.assertIsNotNone(self.ai_model)
        self.assertEqual(self.ai_model.model_type, "gpt4all")
    
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
    
    def test_fallback_mode(self):
        """
        Test fallback response generation.
        """
        # Force fallback mode
        self.ai_model.is_fallback = True
        
        # Test different query types
        hello_response = self.ai_model.generate_response("hello")
        self.assertIn("Hello", hello_response)
        
        help_response = self.ai_model.generate_response("help me")
        self.assertIn("help", help_response.lower())
        
        general_response = self.ai_model.generate_response("random query")
        self.assertIn("basic mode", general_response.lower())

if __name__ == "__main__":
    unittest.main()