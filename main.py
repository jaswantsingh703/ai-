import os
import sys
import threading
import time
import logging
import uuid
import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QTextBrowser, QFileDialog
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant
from src.ai_core.web_browsing import WebBrowsing
from src.ai_core.self_improvement import SelfImprovement
from src.ai_core.image_processing import ImageProcessing
from src.ai_core.video_processing import VideoProcessing
from src.platform_integration.system_control import SystemAutomation
from src.task_management.babyagi_agent import BabyAgiAgent



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AI_GUI(QWidget):
    """Main AI Assistant GUI"""
    def __init__(self):
        super().__init__()
        self.ai_model = AIModel()
        self.voice_assistant = VoiceAssistant()
        self.web_browser = WebBrowsing()
        self.self_improvement = SelfImprovement()
        self.system_control = SystemAutomation()
        self.image_processing = ImageProcessing()
        self.video_processing = VideoProcessing()
        self.task_agent = BabyAgiAgent()
        self.init_ui()

    def init_ui(self):
        """Setup GUI layout"""
        self.setWindowTitle("AI Assistant")
        self.setGeometry(200, 200, 800, 600)
        layout = QVBoxLayout()
        
        self.title_label = QLabel("🤖 AI Assistant")
        self.title_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.title_label)

        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.returnPressed.connect(self.process_input)
        layout.addWidget(self.input_box)

        self.send_button = QPushButton("💬 Send")
        self.send_button.clicked.connect(self.process_input)
        layout.addWidget(self.send_button)

        self.voice_button = QPushButton("🎙️ Speak")
        self.voice_button.clicked.connect(self.start_voice_input)
        layout.addWidget(self.voice_button)

        self.setLayout(layout)

    def process_input(self):
        """Process user input"""
        user_text = self.input_box.text().strip()
        if not user_text:
            return
        self.chat_display.append(f"🗣️ You: {user_text}")
        self.input_box.clear()
        response = self.ai_model.generate_response(user_text)
        self.chat_display.append(f"🤖 AI: {response}")

    def start_voice_input(self):
        """Process voice input"""
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        try:
            text = self.voice_assistant.listen()
            if text:
                self.chat_display.append(f"🗣️ You: {text}")
                response = self.ai_model.generate_response(text)
                self.chat_display.append(f"🤖 AI: {response}")
                self.voice_assistant.speak(response)
        except Exception as e:
            self.chat_display.append(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = AI_GUI()
    main_window.show()
    sys.exit(app.exec_())
