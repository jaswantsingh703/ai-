import unittest
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import AI_GUI
import sys

class TestGUI(unittest.TestCase):
    """
    Unit tests for the AI GUI functionalities.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Setup before running the GUI tests.
        """
        cls.app = QApplication(sys.argv)
    
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
    
    def test_gui_text_input(self):
        """
        Test if text input field exists.
        """
        self.assertIsNotNone(self.gui.input_box)
    
    def test_gui_response_display(self):
        """
        Test if response display exists.
        """
        self.assertIsNotNone(self.gui.chat_display)
    
    @classmethod
    def tearDownClass(cls):
        """
        Cleanup after all tests.
        """
        cls.app.quit()

if __name__ == "__main__":
    unittest.main()
