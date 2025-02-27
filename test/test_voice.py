import unittest
from src.ai_core.voice_processing import VoiceAssistant

class TestVoiceAssistant(unittest.TestCase):
    """
    Unit tests for the Voice Assistant functionalities.
    """
    
    def setUp(self):
        """
        Setup Voice Assistant instance before each test.
        """
        self.voice_assistant = VoiceAssistant()
    
    def test_voice_recognition(self):
        """
        Test if voice recognition module works correctly.
        """
        result = self.voice_assistant.listen()
        self.assertIsInstance(result, str)
    
    def test_voice_response(self):
        """
        Test if voice response function executes without error.
        """
        try:
            self.voice_assistant.speak("Testing voice response.")
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
if __name__ == "__main__":
    unittest.main()
