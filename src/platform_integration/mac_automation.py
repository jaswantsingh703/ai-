import os
import logging
import subprocess

class MacAutomation:
    def __init__(self):
        """
        Initialize Mac-specific automation functions.
        """
        logging.info("Mac Automation module initialized.")

    def open_application(self, app_name):
        """
        Open an application on macOS.
        :param app_name: Name of the application to open.
        """
        try:
            os.system(f"open -a '{app_name}'")
            logging.info(f"Opened application: {app_name}")
        except Exception as e:
            logging.error(f"Error opening application {app_name}: {e}")
            return str(e)

    def execute_command(self, command):
        """
        Execute a shell command on macOS.
        :param command: Shell command to execute.
        """
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            logging.info(f"Executed command: {command}")
            return result.stdout
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            return str(e)

    def shutdown(self):
        """
        Shutdown the Mac system.
        """
        logging.info("Shutting down system...")
        os.system("sudo shutdown -h now")

    def restart(self):
        """
        Restart the Mac system.
        """
        logging.info("Restarting system...")
        os.system("sudo reboot")

    def change_volume(self, level):
        """
        Change the system volume.
        :param level: Volume level (0-100).
        """
        try:
            os.system(f"osascript -e 'set volume output volume {level}'")
            logging.info(f"Changed volume to: {level}")
        except Exception as e:
            logging.error(f"Error changing volume: {e}")
            return str(e)

    def get_brightness(self):
        """
        Get the current screen brightness level.
        """
        try:
            result = subprocess.run(["brightness", "-l"], capture_output=True, text=True)
            logging.info("Fetched brightness level.")
            return result.stdout
        except Exception as e:
            logging.error(f"Error getting brightness: {e}")
            return str(e)

    def set_brightness(self, level):
        """
        Set the screen brightness.
        :param level: Brightness level (0.0 - 1.0).
        """
        try:
            os.system(f"brightness {level}")
            logging.info(f"Set brightness to: {level}")
        except Exception as e:
            logging.error(f"Error setting brightness: {e}")
            return str(e)

# Example Usage
if __name__ == "__main__":
    mac_auto = MacAutomation()
    mac_auto.open_application("Safari")
    mac_auto.execute_command("ls -l")
    # mac_auto.shutdown() # Be careful when uncommenting
    # mac_auto.restart()