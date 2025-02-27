import os
import sys
import logging
import argparse
from src.utils.config import Config
from src.utils.error_handler import ErrorHandler
from src.main_controller import AIAssistantController
from PyQt5.QtWidgets import QApplication

# Set up error handling
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    filename="logs/ai_logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def main():
    """
    Main function to start the AI Assistant.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Assistant")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["cli", "voice", "gui", "automation"],
        default="gui",
        help="Choose the mode: cli, voice, gui, automation",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file",
    )
    args = parser.parse_args()

    # Load configuration
    Config.load(args.config)
    
    # Start the AI Assistant
    try:
        if args.mode == "gui":
            app = QApplication(sys.argv)
            assistant = AIAssistantController(mode=args.mode)
            assistant.run()
            sys.exit(app.exec_())
        else:
            assistant = AIAssistantController(mode=args.mode)
            assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Exiting AI Assistant...")
    except Exception as e:
        logging.error(f"Error starting AI Assistant: {e}")
        print(f"❌ Error starting AI Assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()