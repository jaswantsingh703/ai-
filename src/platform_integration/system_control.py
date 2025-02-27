import os
import platform
import logging
import subprocess
import shlex
import re
from src.utils.config import Config

class SystemControl:
    """
    Secure system control with proper validation and permission checks.
    """
    
    # List of allowed commands for security
    ALLOWED_COMMANDS = {
        "general": ["echo", "date", "time", "whoami", "hostname"],
        "file": ["ls", "dir", "pwd", "cd", "find", "type", "cat"],
        "network": ["ping", "traceroute", "netstat", "ifconfig", "ipconfig"]
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf", r"format", r"del\s+/", r"deltree",
        r"mkfs", r"fdisk", r"\brm\b.*[^\w]\/", r"dd\b"
    ]
    
    def __init__(self, enable_system_control=None):
        """
        Initialize the System Control module with security checks.
        
        Args:
            enable_system_control (bool): Whether to enable system control
        """
        self.os_type = platform.system()
        
        # Use config if parameter not provided
        if enable_system_control is None:
            self.enable_system_control = Config.get("enable_system_control", False)
        else:
            self.enable_system_control = enable_system_control
        
        logging.info(f"SystemControl initialized for {self.os_type}")
        
        if not self.enable_system_control:
            logging.warning("System control is disabled. Use enable() to enable it.")
    
    def enable(self, confirm=False):
        """
        Enable system control with explicit confirmation.
        
        Args:
            confirm (bool): Confirmation flag
            
        Returns:
            bool: Success status
        """
        if not confirm:
            logging.warning("System control not enabled. Set confirm=True to enable.")
            return False
            
        self.enable_system_control = True
        logging.info("System control enabled")
        return True
    
    def execute_command(self, command):
        """
        Execute system command with security validation.
        
        Args:
            command (str): Command to execute
            
        Returns:
            str: Command output or error message
        """
        if not self.enable_system_control:
            return "System control is disabled for security. Enable it first."
            
        # Validate command for security
        validation_result = self._validate_command(command)
        if validation_result != "valid":
            logging.warning(f"Blocked command: {command}. Reason: {validation_result}")
            return f"Command blocked for security reasons: {validation_result}"
        
        try:
            # Execute command securely using proper methods
            if self.os_type == "Windows":
                # For Windows, use subprocess with shell=False for security
                process = subprocess.run(
                    ["cmd", "/c", command],
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=10
                )
                return process.stdout.strip()
            else:
                # For Unix, use subprocess with shell=False and args list
                args = shlex.split(command)
                process = subprocess.run(
                    args,
                    capture_output=True,
                    text=True,
                    shell=False,
                    timeout=10
                )
                return process.stdout.strip()
                
        except subprocess.TimeoutExpired:
            return "Command execution timed out."
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            return f"Error executing command: {str(e)}"
    
    def _validate_command(self, command):
        """
        Validate a command for security.
        
        Args:
            command (str): Command to validate
            
        Returns:
            str: "valid" or reason for rejection
        """
        if not command or not command.strip():
            return "empty command"
            
        # Check for dangerous patterns using regex
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return "potentially harmful command detected"
        
        # Get the base command (first word)
        base_command = command.split()[0].lower()
        
        # Check if the command is in any of the allowed lists
        for category, allowed_cmds in self.ALLOWED_COMMANDS.items():
            if base_command in allowed_cmds:
                return "valid"
        
        # Check allowed commands from config
        config_allowed_commands = Config.get("allowed_commands", [])
        if base_command in config_allowed_commands:
            return "valid"
        
        # Command not found in any allowed list
        return "command not in allowed list"
    
    def open_application(self, app_name):
        """
        Open an application safely.
        
        Args:
            app_name (str): Name of the application
            
        Returns:
            str: Result message
        """
        if not self.enable_system_control:
            return "System control is disabled for security. Enable it first."
            
        # Validate app name (simple validation)
        if not app_name or ";" in app_name or "&" in app_name or "|" in app_name:
            return "Invalid application name"
        
        try:
            # Platform-specific application opening
            if self.os_type == "Windows":
                os.startfile(app_name)
            elif self.os_type == "Darwin":  # macOS
                subprocess.run(["open", "-a", app_name], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", app_name], check=True)
                
            return f"Application '{app_name}' opened successfully"
            
        except Exception as e:
            logging.error(f"Error opening application: {e}")
            return f"Error opening application: {str(e)}"
    
    def get_system_info(self):
        """
        Get system information safely.
        
        Returns:
            dict: System information
        """
        info = {
            "os": self.os_type,
            "platform": platform.platform(),
            "python": platform.python_version(),
            "processor": platform.processor(),
            "hostname": platform.node()
        }
        
        return info


class SystemAutomation:
    """
    Safe system automation with proper task management.
    """
    
    def __init__(self, enable_automation=None):
        """
        Initialize system automation.
        
        Args:
            enable_automation (bool): Whether to enable automation
        """
        # Use config if parameter not provided
        if enable_automation is None:
            self.enable_automation = Config.get("enable_system_control", False)
        else:
            self.enable_automation = enable_automation
            
        self.system_control = SystemControl(enable_system_control=self.enable_automation)
        self.tasks = []
        
        logging.info("SystemAutomation initialized")
    
    def add_task(self, task_name, command, schedule=None):
        """
        Add a task to the automation queue.
        
        Args:
            task_name (str): Name of the task
            command (str): Command to execute
            schedule (str, optional): Schedule for task execution
            
        Returns:
            bool: Success status
        """
        if not self.enable_automation:
            logging.warning("Automation is disabled. Enable it first.")
            return False
            
        task = {
            "name": task_name,
            "command": command,
            "schedule": schedule,
            "status": "pending"
        }
        
        self.tasks.append(task)
        logging.info(f"Task added: {task_name}")
        return True
    
    def execute_tasks(self):
        """
        Execute all pending tasks.
        
        Returns:
            list: Results of task execution
        """
        if not self.enable_automation:
            return ["Automation is disabled"]
            
        results = []
        
        for task in self.tasks:
            if task["status"] == "pending":
                logging.info(f"Executing task: {task['name']}")
                
                try:
                    result = self.system_control.execute_command(task["command"])
                    task["status"] = "completed"
                    task["result"] = result
                    results.append(f"Task '{task['name']}' completed: {result}")
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    results.append(f"Task '{task['name']}' failed: {e}")
        
        return results
    
    def get_task_status(self):
        """
        Get the status of all tasks.
        
        Returns:
            list: Task status information
        """
        return [{
            "name": task["name"],
            "status": task["status"],
            "schedule": task["schedule"]
        } for task in self.tasks]
    
    def run_task(self, task):
        """
        Run a single task by name.
        
        Args:
            task (str): Task name or command
            
        Returns:
            str: Result message
        """
        logging.info(f"Running task: {task}")
        
        if not self.enable_automation:
            return "Automation is disabled"
            
        # Check if this is a task by name
        for existing_task in self.tasks:
            if existing_task["name"] == task:
                try:
                    result = self.system_control.execute_command(existing_task["command"])
                    existing_task["status"] = "completed"
                    existing_task["result"] = result
                    return f"Task '{task}' completed: {result}"
                except Exception as e:
                    existing_task["status"] = "failed"
                    existing_task["error"] = str(e)
                    return f"Task '{task}' failed: {e}"
        
        # If not a stored task, try to execute as a command
        return self.system_control.execute_command(task)