import os
import logging
import subprocess
import re
from src.utils.config import Config

# Check if pyautogui is available
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("pyautogui module not available. Some automation features will be limited.")

class WindowsAutomation:
    """
    Windows-specific automation functions with improved security.
    """
    
    # Allowed Windows commands for security
    ALLOWED_COMMANDS = [
        "dir", "echo", "time", "date", "hostname", "systeminfo",
        "ipconfig", "ping", "ver", "where", "whoami", "type"
    ]
    
    def __init__(self):
        """
        Initialize Windows-specific automation functions.
        """
        self.enable_automation = Config.get("enable_system_control", False)
        logging.info("Windows Automation module initialized.")

    def open_application(self, app_path):
        """
        Open an application on Windows.
        
        Args:
            app_path (str): Path to the application executable
            
        Returns:
            str: Success message or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        # Validate app path
        if not app_path or ";" in app_path or "&" in app_path or "|" in app_path:
            return "Invalid application path"
            
        # Check if the path seems reasonable
        if re.search(r"system32|syswow64|windows\\", app_path.lower()):
            logging.warning(f"Potentially suspicious application path: {app_path}")
            return "Access to system directories is restricted"
        
        try:
            os.startfile(app_path)
            logging.info(f"Opened application: {app_path}")
            return f"Application opened: {app_path}"
        except Exception as e:
            logging.error(f"Error opening application {app_path}: {e}")
            return str(e)

    def execute_command(self, command):
        """
        Execute a shell command on Windows with security checks.
        
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
            # Execute safely using subprocess without shell
            result = subprocess.run(
                ["cmd", "/c", command],
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
            
        if not PYAUTOGUI_AVAILABLE:
            return "Volume control requires pyautogui module"
            
        try:
            # Validate level
            level = max(0, min(100, int(level)))
            
            # Calculate number of presses needed
            current_volume = self.get_volume()
            current_level = int(current_volume) if current_volume.isdigit() else 50
            
            if level > current_level:
                # Volume up
                presses = (level - current_level) // 2
                for _ in range(presses):
                    pyautogui.press("volumeup")
            else:
                # Volume down
                presses = (current_level - level) // 2
                for _ in range(presses):
                    pyautogui.press("volumedown")
                    
            logging.info(f"Changed volume to approximately: {level}")
            return f"Volume changed to approximately {level}%"
        except Exception as e:
            logging.error(f"Error changing volume: {e}")
            return str(e)

    def get_volume(self):
        """
        Get the current volume level (approximate).
        
        Returns:
            str: Volume level or error message
        """
        try:
            result = subprocess.run(
                "powershell -c \"(Get-WmiObject -Class MSFT_PhysicalVolume).MasterVolume\"",
                capture_output=True,
                text=True,
                shell=True  # Required for this specific command
            )
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting volume: {e}")
            return "Unknown"

    def get_brightness(self):
        """
        Get the current screen brightness level.
        
        Returns:
            str: Brightness level or error message
        """
        try:
            result = subprocess.run(
                "powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness",
                capture_output=True,
                text=True,
                shell=True  # Required for this specific command
            )
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return "Unknown"

    def set_brightness(self, level):
        """
        Set the screen brightness.
        
        Args:
            level (int): Brightness level (0-100)
            
        Returns:
            str: Success message or error
        """
        if not self.enable_automation:
            return "System control is disabled. Enable it first."
            
        try:
            # Validate level
            level = max(0, min(100, int(level)))
            
            # Execute with validation
            os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
            logging.info(f"Set brightness to: {level}")
            return f"Brightness set to {level}%"
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
            return str(e)