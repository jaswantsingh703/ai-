import os
import logging
import subprocess
import re
from src.utils.config import Config

class MacAutomation:
    """
    Mac-specific automation functions with improved security.
    """
    
    # Allowed macOS commands for security
    ALLOWED_COMMANDS = [
        "ls", "echo", "date", "hostname", "sw_vers",
        "ifconfig", "ping", "whoami", "cat"
    ]
    
    def __init__(self):
        """
        Initialize Mac-specific automation functions.
        """
        self.enable_automation = Config.get("enable_system_control", False)
        logging.info("Mac Automation module initialized.")

    def open_application(self, app_name):
        """
        Open an application on macOS.
        
        Args:
            app_name (str): Name of the application to open
            
        Returns:
            str: Success message or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        # Validate app name
        if not app_name or ";" in app_name or "&" in app_name or "|" in app_name:
            return "Invalid application name"
        
        try:
            subprocess.run(["open", "-a", app_name], check=True)
            logging.info(f"Opened application: {app_name}")
            return f"Application opened: {app_name}"
        except Exception as e:
            logging.error(f"Error opening application {app_name}: {e}")
            return str(e)

    def execute_command(self, command):
        """
        Execute a shell command on macOS with security checks.
        
        Args:
            command (str): Command to execute
            
        Returns:
            str: Command output or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        # Validate command
        base_command = command.split()[0].lower()
        if base_command not in self.ALLOWED_COMMANDS:
            logging.warning(f"Blocked command: {command}")
            return "Command not allowed for security reasons"
        
        try:
            # Execute safely using subprocess
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            logging.info(f"Executed command: {command}")
            return result.stdout
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            return str(e)

    def change_volume(self, level):
        """
        Change the system volume.
        
        Args:
            level (int): Volume level (0-100)
            
        Returns:
            str: Success message or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        try:
            # Validate level
            level = max(0, min(100, int(level)))
            
            # Convert to macOS volume scale (0-10)
            mac_volume = level / 10
            
            # Set volume using AppleScript
            os.system(f'osascript -e "set volume output volume {level}"')
            logging.info(f"Changed volume to: {level}")
            return f"Volume changed to {level}%"
        except Exception as e:
            logging.error(f"Error changing volume: {e}")
            return str(e)

    def get_brightness(self):
        """
        Get the current screen brightness level.
        
        Returns:
            str: Brightness level or error message
        """
        try:
            # This command requires the 'brightness' utility to be installed
            result = subprocess.run(
                ["brightness", "-l"],
                capture_output=True,
                text=True
            )
            # Extract brightness value from output
            output = result.stdout
            brightness_match = re.search(r"brightness (\d+(\.\d+)?)%", output)
            if brightness_match:
                return brightness_match.group(1)
            return "Unknown"
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return "Unknown (brightness utility not installed)"

    def set_brightness(self, level):
        """
        Set the screen brightness.
        
        Args:
            level (float): Brightness level (0.0-1.0)
            
        Returns:
            str: Success message or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        try:
            # Validate level
            level = max(0.0, min(1.0, float(level)))
            
            # This command requires the 'brightness' utility to be installed
            subprocess.run(["brightness", str(level)], check=True)
            logging.info(f"Set brightness to: {level}")
            return f"Brightness set to {level*100}%"
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
            return str(e)