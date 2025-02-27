import logging
import argparse
import sys
from PyQt5.QtWidgets import QApplication
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant
from src.gui.main_window import AI_GUI
from src.gui.voice_gui import VoiceGUI
from src.platform_integration.system_control import SystemAutomation
from src.database.user_data import UserData
from src.security.ai_security import AISecurity
from src.utils.config import Config
from src.utils.error_handler import ErrorHandler

class AIAssistantController:
    """
    Main AI Assistant Controller that manages all modules.
    """

    def __init__(self, mode="cli"):
        """
        Initialize the AI Assistant Controller.
        
        Args:
            mode (str): Operating mode - "cli", "voice", "gui", or "automation"
        """
        self.mode = mode
        
        # Initialize core components
        try:
            self.ai_model = AIModel(model_type=Config.get("default_model_type"))
            self.voice_assistant = VoiceAssistant()
            self.system_automation = SystemAutomation()
            self.user_data = UserData()
            self.ai_security = AISecurity()
            
            # Initialize GUI if needed
            self.gui = None
            if self.mode == "gui":
                self.gui = AI_GUI()
                
            logging.info(f"AI Assistant Controller initialized in {mode} mode")
        except Exception as e:
            logging.error(f"Error initializing AI Assistant Controller: {e}")
            print(f"Error initializing AI Assistant: {e}")

    def run_cli(self):
        """
        Run AI Assistant in command line interface mode.
        """
        print("🔹 AI Assistant CLI Mode Activated! Type 'exit' to quit.")
        print("🤖 AI: Hello! How can I help you today?")
        
        while True:
            try:
                # Get user input
                user_input = input("🗨️ You: ")
                
                # Check for exit command
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("👋 Exiting AI Assistant...")
                    break
                
                # Process input through security filter
                is_valid, filtered_input = self.ai_security.validate_input(user_input)
                if not is_valid:
                    print(f"⚠️ AI: {filtered_input}")
                    continue
                
                # Generate response
                response = self.ai_model.generate_response(filtered_input)
                
                # Filter response through security
                safe_response = self.ai_security.filter_response(response)
                
                # Store interaction
                self.user_data.store_user_query("cli_user", user_input, safe_response)
                
                # Display response
                print(f"🤖 AI: {safe_response}")
                
            except KeyboardInterrupt:
                print("\n👋 Exiting AI Assistant...")
                break
            except Exception as e:
                logging.error(f"Error in CLI mode: {e}")
                print(f"❌ Error: {str(e)}")

    def run_voice(self):
        """
        Run AI Assistant in voice interface mode.
        """
        print("🎤 Voice Assistant Mode Activated. Speak 'exit' to stop.")
        print("🤖 AI: Hello! I'm listening for voice commands.")
        
        while True:
            try:
                # Listen for speech
                print("🎤 Listening...")
                text = self.voice_assistant.listen()
                
                if not text:
                    print("❓ Sorry, I didn't catch that.")
                    continue
                    
                print(f"🗣️ You: {text}")
                
                # Check for exit command
                if text.lower() in ["exit", "quit", "bye", "stop"]:
                    print("👋 Stopping Voice Assistant...")
                    break
                
                # Process input through security filter
                is_valid, filtered_input = self.ai_security.validate_input(text)
                if not is_valid:
                    response = filtered_input
                else:
                    # Generate response
                    response = self.ai_model.generate_response(filtered_input)
                    
                # Filter response through security
                safe_response = self.ai_security.filter_response(response)
                
                # Store interaction
                self.user_data.store_user_query("voice_user", text, safe_response)
                
                # Display and speak response
                print(f"🤖 AI: {safe_response}")
                self.voice_assistant.speak(safe_response)
                
            except KeyboardInterrupt:
                print("\n👋 Exiting Voice Assistant...")
                break
            except Exception as e:
                logging.error(f"Error in voice mode: {e}")
                print(f"❌ Error: {str(e)}")

    def run_gui(self):
        """
        Run AI Assistant in graphical user interface mode.
        """
        print("🖥️ Launching AI Assistant GUI...")
        if self.gui:
            self.gui.show()
        else:
            print("❌ Error: GUI not initialized.")

    def run_system_automation(self):
        """
        Run AI Assistant in system automation mode.
        """
        print("⚙️ Running System Automation Tasks...")
        try:
            results = self.system_automation.execute_tasks()
            for result in results:
                print(result)
        except Exception as e:
            logging.error(f"Error in automation mode: {e}")
            print(f"❌ Error: {str(e)}")

    def run(self):
        """
        Run AI Assistant in the selected mode.
        """
        try:
            if self.mode == "cli":
                self.run_cli()
            elif self.mode == "voice":
                self.run_voice()
            elif self.mode == "gui":
                self.run_gui()
            elif self.mode == "automation":
                self.run_system_automation()
            else:
                print(f"❌ Invalid mode: {self.mode}. Use 'cli', 'voice', 'gui', or 'automation'.")
        except Exception as e:
            logging.error(f"Error running AI Assistant: {e}")
            print(f"❌ Error: {str(e)}")

    def process_query(self, user_id, query, context=None):
        """
        Process a user query and return a secure response.
        
        Args:
            user_id (str): User identifier
            query (str): User query text
            context (str, optional): Additional context
            
        Returns:
            str: AI response
        """
        try:
            # Validate input
            is_valid, filtered_input = self.ai_security.validate_input(query)
            if not is_valid:
                return filtered_input
                
            # Generate response with context if provided
            if context:
                response = self.ai_model.generate_response(f"{context}\n\nUser query: {filtered_input}")
            else:
                response = self.ai_model.generate_response(filtered_input)
                
            # Filter response for security
            secure_response = self.ai_security.filter_response(response)
            
            # Store interaction
            self.user_data.store_user_query(user_id, query, secure_response)
            
            return secure_response
            
        except Exception as e:
            logging.error(f"Error processing query: {e}")
            return "I'm sorry, I encountered an error while processing your request."