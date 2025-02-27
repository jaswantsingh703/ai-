import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt5.QtGui import QFont
from src.ai_core.voice_processing import VoiceAssistant

class VoiceGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.voice_assistant = VoiceAssistant()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Voice Assistant")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()

        self.title_label = QLabel("🎤 Voice Assistant")
        self.title_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.title_label)

        self.status_label = QLabel("🟢 Ready")
        self.status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.status_label)

        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)

        self.speak_button = QPushButton("🎙️ Speak")
        self.speak_button.setFont(QFont("Arial", 12))
        self.speak_button.clicked.connect(self.start_voice_input)
        layout.addWidget(self.speak_button)

        self.setLayout(layout)

    def start_voice_input(self):
        self.status_label.setText("🎤 Listening...")
        self.speak_button.setEnabled(False)
        threading.Thread(target=self.process_voice_input, daemon=True).start()

    def process_voice_input(self):
        try:
            text = self.voice_assistant.listen()
            if text:
                self.output_display.append(f"🗣️ You: {text}")
                response = f"Processing command: {text}"
                self.output_display.append(f"🤖 AI: {response}")
                self.voice_assistant.speak(response)
        except Exception as e:
            self.output_display.append(f"❌ Error: {str(e)}")
        self.status_label.setText("🟢 Ready")
        self.speak_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceGUI()
    window.show()
    sys.exit(app.exec_())