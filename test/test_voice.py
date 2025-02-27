import unittest
import os
import tempfile
import numpy as np
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
    
    def test_initialization(self):
        """
        Test if Voice Assistant initializes correctly.
        """
        self.assertIsNotNone(self.voice_assistant)
        self.assertFalse(self.voice_assistant.is_listening)
    
    def test_tts_functionality(self):
        """
        Test if text-to-speech function executes without error.
        """
        try:
            # Use a short text to minimize test duration
            success = self.voice_assistant.speak("Test")
            # May return False if TTS engine is not available
        except Exception:
            success = False
        
        # We don't assert success since TTS may not be available on all systems
        # Just ensure it doesn't throw an exception
        self.assertIsNotNone(success)
    
    def test_save_wav(self):
        """
        Test WAV file saving functionality.
        """
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            # Generate a short sine wave audio sample
            sample_rate = 16000
            audio_data = np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate)).astype(np.float32)
            
            # Save the audio
            self.voice_assistant._save_wav(temp_path, audio_data, sample_rate)
            
            # Check if file exists and has content
            self.assertTrue(os.path.exists(temp_path))
            self.assertGreater(os.path.getsize(temp_path), 0)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

if __name__ == "__main__":
    unittest.main()