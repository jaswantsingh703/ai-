import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.setGeometry(200, 200, 600, 500)

        self.ai_model = AIModel()
        self.voice_assistant = VoiceAssistant()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        self.input_box = QTextEdit()
        layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        layout.addWidget(self.send_button)

        self.voice_button = QPushButton("Speak")
        self.voice_button.clicked.connect(self.process_voice)
        layout.addWidget(self.voice_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def process_input(self):
        user_text = self.input_box.toPlainText().strip()
        if not user_text:
            return
        self.text_display.append(f"User: {user_text}")
        response = self.ai_model.generate_response(user_text)
        self.text_display.append(f"AI: {response}")
        self.input_box.clear()

    def process_voice(self):
        self.text_display.append("Listening...")
        text = self.voice_assistant.listen()
        if text:
            self.text_display.append(f"User: {text}")
            response = self.ai_model.generate_response(text)
            self.text_display.append(f"AI: {response}")
            self.voice_assistant.speak(response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())