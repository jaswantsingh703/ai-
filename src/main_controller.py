import logging
import os
import sys
import threading
from PyQt5.QtWidgets import QApplication
from src.ai_core.model_integration import AIModel
from src.ai_core.voice_processing import VoiceAssistant
from src.ai_core.web_browsing import WebBrowsing
from src.ai_core.image_processing import ImageProcessing
from src.ai_core.video_processing import VideoProcessing
from src.ai_core.self_improvement import SelfImprovement
from src.ai_core.hacking_lab import HackingLab
from src.ai_core.real_time_learning import SelfLearningAI
from src.gui.main_window import AI_GUI
from src.gui.voice_gui import VoiceGUI
from src.platform_integration.system_control import SystemAutomation, SystemControl
from src.task_management.babyagi_agent import TaskScheduler
from src.database.user_data import UserData
from src.security.ai_security import AISecurity
from src.utils.config import Config
from src.utils.helper_functions import get_current_timestamp

class AIAssistantController:
    """
    Main controller class for the AI Assistant.
    Integrates all components and manages their interactions.
    """
    
    def __init__(self, mode="gui"):
        """
        Initialize the AI Assistant with all its components.
        
        Args:
            mode (str): Operating mode - "cli", "voice", "gui", or "automation"
        """
        self.mode = mode
        logging.info(f"Starting AI Assistant in {mode} mode")
        
        # Set up components
        self._setup_components()
        
        # Initialize command handlers
        self._init_command_handlers()
        
        logging.info("AI Assistant Controller initialized")
        print(f"🤖 Jarvis AI initialized in {mode} mode")
    
    def _setup_components(self):
        """Set up all AI Assistant components."""
        try:
            # Initialize AI models and voice processing
            self.ai_model = AIModel(model_type=Config.get("default_model_type"))
            self.voice_assistant = VoiceAssistant()
            
            # Initialize utility modules
            self.web_browser = WebBrowsing()
            self.image_processor = ImageProcessing()
            self.video_processor = VideoProcessing()
            self.self_improvement = SelfImprovement()
            self.hacking_lab = HackingLab()
            self.memory = SelfLearningAI()
            
            # Initialize system automation
            self.system_automation = SystemAutomation()
            self.system_control = SystemControl()
            
            # Initialize task management
            self.task_scheduler = TaskScheduler()
            
            # Initialize security and user data
            self.security = AISecurity()
            self.user_data = UserData()
            
            # Initialize GUI if needed
            self.gui = None
            if self.mode == "gui":
                self.gui = AI_GUI()
            elif self.mode == "voice":
                self.gui = VoiceGUI()
                
        except Exception as e:
            logging.error(f"Error setting up components: {e}")
            print(f"❌ Error initializing components: {e}")
            
    def _init_command_handlers(self):
        """Initialize command handlers for different voice commands."""
        self.command_handlers = {
            "open": self._handle_open_command,
            "search": self._handle_search_command,
            "run": self._handle_run_command,
            "detect": self._handle_detect_command,
            "extract": self._handle_extract_command,
            "improve": self._handle_improve_command,
            "add task": self._handle_add_task_command,
            "show tasks": self._handle_show_tasks_command,
            "help": self._handle_help_command
        }
    
    def run(self):
        """
        Run the AI Assistant in the selected mode.
        """
        try:
            if self.mode == "cli":
                self._run_cli_mode()
            elif self.mode == "voice":
                self._run_voice_mode()
            elif self.mode == "gui":
                self._run_gui_mode()
            elif self.mode == "automation":
                self._run_automation_mode()
            else:
                print(f"❌ Invalid mode: {self.mode}")
        except Exception as e:
            logging.error(f"Error running AI Assistant: {e}")
            print(f"❌ Error: {e}")
    
    def _run_cli_mode(self):
        """Run AI Assistant in command-line interface mode."""
        print("🔹 AI Assistant CLI Mode")
        print("🤖 Jarvis: I'm ready to assist you. Type 'exit' to quit.")
        
        while True:
            try:
                # Get user input
                user_input = input("🗣️ You: ")
                
                # Exit condition
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("👋 Goodbye!")
                    break
                
                # Process the command
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logging.error(f"Error in CLI mode: {e}")
                print(f"❌ Error: {e}")
    
    def _run_voice_mode(self):
        """Run AI Assistant in voice-controlled mode."""
        print("🎤 Voice Assistant Mode")
        print("🤖 Jarvis: Say 'exit' to quit.")
        
        while True:
            try:
                # Listen for a command
                print("🎤 Listening...")
                command = self.voice_assistant.listen()
                
                if not command:
                    print("❓ I didn't catch that.")
                    continue
                
                print(f"🗣️ You: {command}")
                
                # Exit condition
                if command.lower() in ["exit", "quit", "bye", "goodbye"]:
                    response = "Goodbye!"
                    print(f"🤖 Jarvis: {response}")
                    self.voice_assistant.speak(response)
                    break
                
                # Process the command
                self._process_command(command, voice_response=True)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logging.error(f"Error in voice mode: {e}")
                print(f"❌ Error: {e}")
                
    def _run_gui_mode(self):
        """Run AI Assistant in GUI mode."""
        if self.gui:
            self.gui.show()
        else:
            print("❌ GUI not initialized.")
    
    def _run_automation_mode(self):
        """Run AI Assistant in automation mode."""
        print("⚙️ Running automation tasks...")
        
        # Execute scheduled tasks
        results = self.system_automation.execute_tasks()
        for result in results:
            print(result)
    
    def _process_command(self, command, voice_response=False):
        """
        Process a user command and execute corresponding action.
        
        Args:
            command (str): User command text
            voice_response (bool): Whether to also speak the response
        """
        # Validate command through security filter
        is_valid, filtered_command = self.security.validate_input(command)
        if not is_valid:
            response = filtered_command  # This will be an error message
            print(f"🤖 Jarvis: {response}")
            if voice_response:
                self.voice_assistant.speak(response)
            return
        
        command_lower = filtered_command.lower()
        
        # Check for specific command patterns
        for cmd_key, handler in self.command_handlers.items():
            if cmd_key in command_lower:
                response = handler(filtered_command)
                print(f"🤖 Jarvis: {response}")
                if voice_response:
                    self.voice_assistant.speak(response)
                return
        
        # Default: use AI model for general response
        context = self.memory.get_combined_context(filtered_command)
        response = self.ai_model.generate_response(context)
        
        # Store the interaction
        self.memory.store_interaction(filtered_command, response)
        self.user_data.store_user_query("user", filtered_command, response)
        
        print(f"🤖 Jarvis: {response}")
        if voice_response:
            self.voice_assistant.speak(response)
    
    def _handle_open_command(self, command):
        """Handle commands to open applications."""
        # Extract the application name
        # Pattern: "open [app name]"
        parts = command.lower().split("open ", 1)
        if len(parts) < 2:
            return "What would you like me to open?"
        
        app_name = parts[1].strip()
        result = self.system_control.open_application(app_name)
        return result
    
    def _handle_search_command(self, command):
        """Handle web search commands."""
        # Extract the search query
        # Pattern: "search [query]"
        parts = command.lower().split("search ", 1)
        if len(parts) < 2:
            return "What would you like me to search for?"
        
        query = parts[1].strip()
        
        # Perform search
        search_results = self.web_browser.google_search(query)
        
        # Summarize results
        if search_results and isinstance(search_results, list):
            content = f"Here are the top results for '{query}':\n"
            for i, url in enumerate(search_results[:3], 1):
                content += f"{i}. {url}\n"
                
            # Try to get content from the first result
            if search_results:
                try:
                    page_content = self.web_browser.fetch_page_content(search_results[0])
                    summary = self.ai_model.generate_response(f"Summarize this content briefly: {page_content[:5000]}")
                    content += f"\nSummary of top result: {summary}"
                except:
                    pass
                    
            return content
        else:
            return f"I couldn't find any results for '{query}'."
    
    def _handle_run_command(self, command):
        """Handle commands to run specific features."""
        command_lower = command.lower()
        
        if "port scan" in command_lower or "ping sweep" in command_lower:
            # Run hacking lab features with safety checks
            if "port scan" in command_lower:
                target = "127.0.0.1"  # Default to localhost for safety
                if "on " in command_lower:
                    parts = command_lower.split("on ", 1)
                    if len(parts) > 1:
                        target = parts[1].strip()
                return self.hacking_lab.run_port_scan(target)
            
            elif "ping sweep" in command_lower:
                subnet = "192.168.1.0/24"  # Default subnet
                if "on " in command_lower:
                    parts = command_lower.split("on ", 1)
                    if len(parts) > 1:
                        subnet = parts[1].strip()
                results = self.hacking_lab.perform_ping_sweep(subnet)
                return f"Ping sweep found {len(results)} live hosts: {', '.join(results[:5])}" + (" and more..." if len(results) > 5 else "")
            
        elif "babyagi" in command_lower or "tasks" in command_lower:
            # Run task manager
            self.task_scheduler.start()
            return "Task scheduler started. It will execute all scheduled tasks."
            
        elif "system" in command_lower:
            # Get system information
            info = self.system_control.get_system_info()
            return f"System Information:\nOS: {info['os']}\nHostname: {info['hostname']}\nPlatform: {info['platform']}\nProcessor: {info['processor']}"
            
        else:
            return "I'm not sure what you want me to run. Try 'run port scan', 'run tasks', or 'run system info'."
    
    def _handle_detect_command(self, command):
        """Handle detection commands for images and videos."""
        command_lower = command.lower()
        
        if "faces" in command_lower:
            # Pattern: "detect faces in [file]"
            if "in " in command_lower:
                file_path = command_lower.split("in ", 1)[1].strip()
                
                # Check if it's a video or image
                if any(file_path.endswith(ext) for ext in ['.mp4', '.avi', '.mov']):
                    results = self.video_processor.detect_faces_in_video(file_path)
                    if "error" in results:
                        return f"Error detecting faces: {results['error']}"
                    return f"Detected faces in {results['frames_with_faces']} of {results['total_frames']} frames. Maximum faces in a single frame: {results['max_faces']}"
                else:
                    faces = self.image_processor.detect_faces(file_path)
                    return f"Detected {len(faces)} faces in the image."
            else:
                return "Please specify an image or video file."
        else:
            return "What would you like me to detect? Try 'detect faces in [filename]'."
    
    def _handle_extract_command(self, command):
        """Handle extraction commands for images."""
        command_lower = command.lower()
        
        if "text" in command_lower and "from" in command_lower:
            # Pattern: "extract text from [file]"
            file_path = command_lower.split("from ", 1)[1].strip()
            
            text = self.image_processor.extract_text(file_path)
            if text and len(text) > 0:
                return f"Extracted text: {text}"
            else:
                return "No text was found in the image or the file could not be processed."
        else:
            return "What would you like me to extract? Try 'extract text from [filename]'."
    
    def _handle_improve_command(self, command):
        """Handle self-improvement commands."""
        command_lower = command.lower()
        
        if "yourself" in command_lower:
            # Generate a new tool
            description = "A utility tool for the AI Assistant"
            if "for " in command_lower:
                description = command_lower.split("for ", 1)[1].strip()
                
            generated_code = self.self_improvement.generate_code(description)
            file_path = self.self_improvement.save_generated_code(f"ai_generated_{get_current_timestamp().replace(' ', '_').replace(':', '')}.py", generated_code)
            
            if file_path:
                return f"I've created a new tool for {description}. You can find it at {file_path}"
            else:
                return "I couldn't create the tool. Please check the logs for details."
        else:
            return "How would you like me to improve? Try 'improve yourself by creating a tool for [description]'."
    
    def _handle_add_task_command(self, command):
        """Handle commands to add tasks."""
        command_lower = command.lower()
        
        if ":" in command_lower:
            # Pattern: "add task: [task description]"
            task = command_lower.split(":", 1)[1].strip()
            
            # Add to task scheduler
            self.task_scheduler.add_task(lambda: print(f"Executing task: {task}"), 3600, task_name=task)
            
            return f"Task added: {task}. It will be scheduled for execution."
        else:
            return "Please provide a task description. For example, 'add task: generate a weekly report'."
    
    def _handle_show_tasks_command(self, command):
        """Handle commands to show tasks."""
        tasks = self.task_scheduler.get_tasks()
        
        if tasks:
            task_list = "\n".join([f"{i+1}. {t['name']} - {'Enabled' if t['enabled'] else 'Disabled'}" for i, t in enumerate(tasks)])
            return f"Current tasks:\n{task_list}"
        else:
            return "No tasks are currently scheduled."
    
    def _handle_help_command(self, command):
        """Handle help commands."""
        return """I can help you with various tasks. Try these commands:
- "Open [application]" - Opens an application
- "Search [query]" - Performs a web search
- "Run port scan" - Performs a network port scan
- "Run tasks" - Executes scheduled tasks
- "Detect faces in [file]" - Detects faces in an image or video
- "Extract text from [image]" - Extracts text from an image
- "Improve yourself by creating a tool for [description]" - Generates a new tool
- "Add task: [description]" - Adds a new task to the scheduler
- "Show tasks" - Displays all scheduled tasks"""