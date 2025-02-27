import os
import logging
import subprocess
import re
from src.utils.config import Config

class LinuxAutomation:
    """
    Linux-specific automation functions with improved security.
    """
    
    # Allowed Linux commands for security
    ALLOWED_COMMANDS = [
        "ls", "echo", "date", "hostname", "uname",
        "ifconfig", "ping", "whoami", "cat"
    ]
    
    def __init__(self):
        """
        Initialize Linux-specific automation functions.
        """
        self.enable_automation = Config.get("enable_system_control", False)
        logging.info("Linux Automation module initialized.")

    def open_application(self, app_name):
        """
        Open an application on Linux.
        
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
            subprocess.Popen(["xdg-open", app_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logging.info(f"Opened application: {app_name}")
            return f"Application opened: {app_name}"
        except Exception as e:
            logging.error(f"Error opening application {app_name}: {e}")
            return str(e)

    def execute_command(self, command):
        """
        Execute a shell command on Linux with security checks.
        
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
            
            # Try to set volume using amixer (ALSA)
            os.system(f"amixer sset 'Master' {level}%")
            logging.info(f"Changed volume to: {level}%")
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
            # Try to get brightness using xrandr
            result = subprocess.run(
                "xrandr --verbose | grep -i brightness",
                shell=True,
                capture_output=True,
                text=True
            )
            logging.info("Fetched brightness level")
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return str(e)

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
            
            # Try to set brightness using xrandr
            # Get the primary display first
            display_cmd = "xrandr | grep ' connected' | cut -d' ' -f1"
            display_result = subprocess.run(display_cmd, shell=True, capture_output=True, text=True)
            display = display_result.stdout.strip()
            
            if display:
                os.system(f"xrandr --output {display} --brightness {level}")
                logging.info(f"Set brightness to: {level}")
                return f"Brightness set to {level*100}%"
            else:
                return "Could not determine display name"
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
            return str(e)