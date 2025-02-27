import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QWidget
from PyQt5.QtGui import QFont
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant
from src.ai_core.web_browsing import WebBrowsing
from src.ai_core.self_improvement import SelfImprovement
from src.ai_core.image_processing import ImageProcessing
from src.ai_core.video_processing import VideoProcessing
from src.utils.config import Config

class AI_GUI(QWidget):
    """
    Main AI Assistant GUI window.
    """
    def __init__(self):
        super().__init__()
        # Initialize AI components
        try:
            self.ai_model = AIModel(model_type=Config.get("default_model_type"))
            self.voice_assistant = VoiceAssistant()
            self.web_browser = WebBrowsing()
            self.self_improvement = SelfImprovement()
            self.image_processing = ImageProcessing()
            self.video_processing = VideoProcessing()
        except Exception as e:
            print(f"Error initializing AI components: {e}")
        
        # Initialize UI
        self.init_ui()

    def init_ui(self):
        """
        Setup GUI layout.
        """
        self.setWindowTitle("AI Assistant")
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()
        
        # Title label
        self.title_label = QLabel("🤖 AI Assistant")
        self.title_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.title_label)

        # Chat display
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input box
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_box)

        # Send button
        self.send_button = QPushButton("💬 Send")
        self.send_button.clicked.connect(self.process_input)
        layout.addWidget(self.send_button)

        # Voice button
        self.voice_button = QPushButton("🎙️ Speak")
        self.voice_button.clicked.connect(self.start_voice_input)
        layout.addWidget(self.voice_button)

        self.setLayout(layout)
        
        # Add welcome message
        self.chat_display.append("🤖 AI: Hello! How can I help you today?")

    def process_input(self):
        """
        Process user text input.
        """
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        
        # Display user message
        self.chat_display.append(f"🗣️ You: {user_text}")
        self.input_box.clear()
        
        try:
            # Generate response
            response = self.ai_model.generate_response(user_text)
            self.chat_display.append(f"🤖 AI: {response}")
        except Exception as e:
            self.chat_display.append(f"❌ Error: {str(e)}")

    def start_voice_input(self):
        """
        Process voice input in a separate thread.
        """
        self.voice_button.setEnabled(False)
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        """
        Process voice input and generate response.
        """
        try:
            # Listen for speech
            self.chat_display.append("🎤 Listening...")
            text = self.voice_assistant.listen()
            
            if text:
                # Display recognized text
                self.chat_display.append(f"🗣️ You: {text}")
                
                # Generate response
                response = self.ai_model.generate_response(text)
                self.chat_display.append(f"🤖 AI: {response}")
                
                # Speak response
                self.voice_assistant.speak(response)
            else:
                self.chat_display.append("❓ Sorry, I didn't catch that.")
        except Exception as e:
            self.chat_display.append(f"❌ Error: {str(e)}")
        finally:
            self.voice_button.setEnabled(True)

    def run(self):
        """
        Show the GUI window.
        """
        self.show()