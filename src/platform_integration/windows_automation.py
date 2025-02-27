import os
import logging
import subprocess
import pyautogui

class WindowsAutomation:
    def __init__(self):
        """
        Initialize Windows-specific automation functions.
        """
        logging.info("Windows Automation module initialized.")

    def open_application(self, app_path):
        """
        Open an application on Windows.
        :param app_path: Path to the application executable.
        """
        try:
            os.startfile(app_path)
            logging.info(f"Opened application: {app_path}")
        except Exception as e:
            logging.error(f"Error opening application {app_path}: {e}")
            return str(e)

    def execute_command(self, command):
        """
        Execute a shell command on Windows.
        :param command: Command to execute.
        """
        try:
            result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True)
            logging.info(f"Executed command: {command}")
            return result.stdout
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            return str(e)

    def shutdown(self):
        """
        Shutdown the Windows system.
        """
        logging.info("Shutting down system...")
        os.system("shutdown /s /t 0")

    def restart(self):
        """
        Restart the Windows system.
        """
        logging.info("Restarting system...")
        os.system("shutdown /r /t 0")

    def change_volume(self, level):
        """
        Change the system volume.
        :param level: Volume level (0-100).
        """
        try:
            pyautogui.press("volumeup", presses=level//2)
            logging.info(f"Changed volume to: {level}")
        except Exception as e:
            logging.error(f"Error changing volume: {e}")
            return str(e)

    def get_brightness(self):
        """
        Get the current screen brightness level.
        """
        try:
            result = subprocess.run("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness", capture_output=True, text=True, shell=True)
            logging.info("Fetched brightness level.")
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return str(e)

    def set_brightness(self, level):
        """
        Set the screen brightness.
        :param level: Brightness level (0-100).
        """
        try:
            os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})")
            logging.info(f"Set brightness to: {level}")
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
            return str(e)

# Example Usage
if __name__ == "__main__":
    win_auto = WindowsAutomation()
    win_auto.open_application("notepad.exe")
    win_auto.execute_command("dir")
    # win_auto.shutdown() # Be careful when uncommenting
    # win_auto.restart()