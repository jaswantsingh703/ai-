# Python script
import logging
import argparse
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant
from src.gui.main_window import AI_GUI
from src.platform_integration.system_control import SystemAutomation
from src.database.user_data import UserData
from src.security.ai_security import AISecurity

# लॉगिंग सेटअप
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class AIAssistantController:
    """मुख्य AI असिस्टेंट कंट्रोलर, जो सभी मॉड्यूल्स को मैनेज करता है"""

    def __init__(self, mode="cli"):
        self.mode = mode
        self.ai_model = AIModel()
        self.voice_assistant = VoiceAssistant()
        self.system_automation = SystemAutomation()
        self.gui = None  # GUI लोड करने के लिए
        
        if self.mode == "gui":
            self.gui = AI_GUI()

    def run_cli(self):
        """CLI मोड में AI असिस्टेंट चलाएं"""
        print("🔹 AI Assistant CLI Mode Activated! Type 'exit' to quit.")
        while True:
            user_input = input("🗨️ You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting AI Assistant...")
                break
            response = self.ai_model.generate_response(user_input)
            print(f"🤖 AI: {response}")

    def run_voice(self):
        """वॉयस असिस्टेंट मोड"""
        print("🎤 Voice Assistant Mode Activated. Speak 'exit' to stop.")
        while True:
            text = self.voice_assistant.listen()
            if text.lower() in ["exit", "quit"]:
                print("👋 Stopping Voice Assistant...")
                break
            response = self.ai_model.generate_response(text)
            print(f"🤖 AI: {response}")
            self.voice_assistant.speak(response)

    def run_gui(self):
        """GUI मोड में AI असिस्टेंट चलाएं"""
        print("🖥️ Launching AI Assistant GUI...")
        if self.gui:
            self.gui.run()

    def run_system_automation(self):
        """ऑटोमेशन कमांड्स रन करें"""
        print("⚙️ Running System Automation Tasks...")
        self.system_automation.execute_tasks()

    def run(self):
        """AI असिस्टेंट को सेलेक्टेड मोड में रन करें"""
        if self.mode == "cli":
            self.run_cli()
        elif self.mode == "voice":
            self.run_voice()
        elif self.mode == "gui":
            self.run_gui()
        elif self.mode == "automation":
            self.run_system_automation()
        else:
            print("❌ Invalid mode! Use 'cli', 'voice', 'gui', or 'automation'.")





            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI Assistant in different modes.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["cli", "voice", "gui", "automation"],
        default="cli",
        help="Choose the mode: cli, voice, gui, automation",
    )
    args = parser.parse_args()

    assistant = AIAssistantController(mode=args.mode)
    assistant.run()



    def __init__(self):
        self.user_data = UserData()
        self.ai_security = AISecurity()

    def process_query(self, user_id, query, ai_response):
        """
        यूज़र क्वेरी को प्रोसेस करें और सिक्योर जवाब दें।
        """
        secure_response = self.ai_security.filter_response(ai_response)
        self.user_data.store_user_query(user_id, query, secure_response)
        return secure_response

# **Usage Example**
if __name__ == "__main__":
    controller = MainController()
    response = controller.process_query("user123", "How to hack?", "Hacking is illegal and unethical.")
    print("Processed Response:", response)