import unittest
import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import AI_GUI

class TestGUI(unittest.TestCase):
    """
    Unit tests for the AI GUI functionalities.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Setup before running the GUI tests.
        """
        # Create QApplication instance if needed
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """
        Setup GUI instance before each test.
        """
        self.gui = AI_GUI()
    
    def test_gui_initialization(self):
        """
        Test if GUI initializes correctly.
        """
        self.assertIsNotNone(self.gui)
        self.assertEqual(self.gui.windowTitle(), "AI Assistant")
    
    def test_gui_components(self):
        """
        Test if GUI components exist.
        """
        self.assertIsNotNone(self.gui.chat_display, "Chat display should exist")
        self.assertIsNotNone(self.gui.input_box, "Input box should exist")
        self.assertIsNotNone(self.gui.send_button, "Send button should exist")
        self.assertIsNotNone(self.gui.voice_button, "Voice button should exist")
    
    def test_input_processing(self):
        """
        Test if input processing works without error.
        """
        # Set test input
        self.gui.input_box.setText("Test message")
        
        # Process should not raise error
        try:
            self.gui.process_input()
            success = True
        except:
            success = False
            
        self.assertTrue(success, "Input processing should not cause errors")
        
        # Input should be cleared
        self.assertEqual(self.gui.input_box.text(), "", "Input box should be cleared after processing")

    @classmethod
    def tearDownClass(cls):
        """
        Cleanup after all tests.
        """
        pass

if __name__ == "__main__":
    unittest.main()