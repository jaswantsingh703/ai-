import os
import platform
import logging

# Configure logging
logging.basicConfig(
    filename="system_control.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class SystemControl:
    """
    Class to control system operations like executing commands, shutting down, restarting, and opening applications.
    """

    def __init__(self):
        """
        Initialize the System Control module and detect OS type.
        """
        self.os_type = platform.system()
        logging.info(f"SystemControl initialized for {self.os_type}")

    def execute_command(self, command):
        """
        Execute system commands based on OS type.
        
        :param command: Command to execute
        :return: Output or error message
        """
        try:
            if self.os_type == "Windows":
                result = os.popen(f"cmd /c {command}").read()
            else:
                result = os.popen(command).read()
            logging.info(f"Executed command: {command}")
            return result.strip()
        except Exception as e:
            logging.error(f"Error executing command: {e}")
            return str(e)

    def shutdown(self):
        """
        Shutdown the system.
        """
        try:
            logging.info("Shutting down system...")
            if self.os_type == "Windows":
                os.system("shutdown /s /t 0")
            else:
                os.system("shutdown -h now")
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")

    def restart(self):
        """
        Restart the system.
        """
        try:
            logging.info("Restarting system...")
            if self.os_type == "Windows":
                os.system("shutdown /r /t 0")
            else:
                os.system("reboot")
        except Exception as e:
            logging.error(f"Error during restart: {e}")

    def open_application(self, app_name):
        """
        Open a specified application.
        
        :param app_name: Name of the application to open.
        """
        try:
            if self.os_type == "Windows":
                os.system(f"start {app_name}")
            elif self.os_type == "Darwin":  # macOS
                os.system(f"open -a '{app_name}'")
            else:  # Linux
                os.system(f"xdg-open '{app_name}'")
            logging.info(f"Opened application: {app_name}")
        except Exception as e:
            logging.error(f"Error opening application {app_name}: {e}")
            return str(e)


class SystemAutomation:
    """
    Class to manage automated system tasks.
    """

    def __init__(self):
        logging.info("SystemAutomation Initialized")

    def run_task(self, task):
        """
        Run an automated task.
        
        :param task: Task to execute
        """
        logging.info(f"Running task: {task}")
        print(f"Running task: {task}")


# Example Usage
if __name__ == "__main__":
    sys_control = SystemControl()

    # Test executing a simple command
    output = sys_control.execute_command("echo Hello World")
    print("Command Output:", output)

    # Uncomment the following lines to test system control actions
    # sys_control.shutdown()
    # sys_control.restart()
    # sys_control.open_application("Calculator")  # Change to an existing app on your OS

    # Testing SystemAutomation
    automation = SystemAutomation()
    automation.run_task("Backup files")