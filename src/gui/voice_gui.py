import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtGui import QFont
from src.ai_core.voice_processing import VoiceAssistant
from src.ai_core.model_integration import AIModel

class VoiceGUI(QWidget):
    """
    Voice-focused AI Assistant GUI.
    """
    def __init__(self):
        super().__init__()
        self.voice_assistant = VoiceAssistant()
        self.ai_model = AIModel()
        self.init_ui()

    def init_ui(self):
        """
        Initialize the Voice GUI interface.
        """
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("🎤 Voice Assistant")
        self.title_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.title_label)

        # Status label
        self.status_label = QLabel("🟢 Ready")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)

        # Output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        # Speak button
        self.speak_button = QPushButton("🎙️ Speak")
        self.speak_button.setFont(QFont("Arial", 12))
        self.speak_button.clicked.connect(self.start_voice_input)
        layout.addWidget(self.speak_button)

        self.setLayout(layout)
        
        # Add welcome message
        self.output_display.append("🤖 AI: Hello! I'm listening for voice commands.")

    def start_voice_input(self):
        """
        Start listening for voice input.
        """
        self.status_label.setText("🎤 Listening...")
        self.speak_button.setEnabled(False)
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        """
        Process voice input and generate response.
        """
        try:
            # Listen for speech
            text = self.voice_assistant.listen()
            
            if text:
                # Display recognized text
                self.output_display.append(f"🗣️ You: {text}")
                
                # Generate response
                response = self.ai_model.generate_response(text)
                self.output_display.append(f"🤖 AI: {response}")
                
                # Speak response
                self.voice_assistant.speak(response)
            else:
                self.output_display.append("❓ Sorry, I didn't catch that.")
        except Exception as e:
            self.output_display.append(f"❌ Error: {str(e)}")
        finally:
            self.status_label.setText("🟢 Ready")
            self.speak_button.setEnabled(True)