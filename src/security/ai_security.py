import logging
import re

class AISecurity:
    """
    AI Security & Response Filtering System
    Controls what content the AI can generate and respond to.
    """

    # Expanded list of blocked keywords for better security
    blocked_words = [
        "hacking", "illegal", "violence", "shutdown", "malware", "exploit",
        "password", "steal", "attack", "crack", "inject", "bypass", "breach"
    ]
    
    # Dangerous system commands to block
    blocked_commands = [
        "rm -rf", "format", "del /", "shutdown", "reboot", 
        "sudo", "chmod", "chown", "mkfs", "dd if"
    ]

    def __init__(self):
        """
        Initialize the AI Security module.
        """
        logging.info("AI Security module initialized")

    def filter_response(self, response):
        """
        Filter AI responses to block unauthorized content.
        
        Args:
            response (str): AI response to filter
            
        Returns:
            str: Filtered response
        """
        if not response:
            return ""
            
        response_lower = response.lower()
        
        for word in self.blocked_words:
            if word in response_lower:
                logging.warning(f"Blocked response containing: {word}")
                return "⚠️ I cannot provide this information as it may be used for unauthorized purposes."
        
        return response
    
    def validate_input(self, user_input):
        """
        Validate user input for potential security issues.
        
        Args:
            user_input (str): User input to validate
            
        Returns:
            tuple: (is_valid, message or validated input)
        """
        if not user_input:
            return True, ""
            
        # Check for command injection attempts
        for cmd in self.blocked_commands:
            if cmd in user_input.lower():
                logging.warning(f"Blocked potentially harmful command: {user_input}")
                return False, "For security reasons, I cannot process commands that could potentially harm your system."
        
        # Check for script injection
        if "<script>" in user_input.lower() or "javascript:" in user_input.lower():
            logging.warning(f"Blocked script injection attempt: {user_input}")
            return False, "I've detected potential script injection in your input and cannot process it."
            
        return True, user_input
    
    def check_command_safety(self, command):
        """
        Check if a system command is safe to execute.
        
        Args:
            command (str): Command to check
            
        Returns:
            bool: True if safe, False otherwise
        """
        if not command:
            return False
            
        command_lower = command.lower()
        
        # Check for dangerous commands
        for dangerous_cmd in self.blocked_commands:
            if dangerous_cmd in command_lower:
                logging.warning(f"Blocked dangerous command: {command}")
                return False
        
        # Check for specific patterns using regex
        dangerous_patterns = [
            r"rm\s+-rf",  # Remove recursively and force
            r"sudo",      # Superuser commands
            r"chmod\s+777", # Dangerous permission changes
            r"mkfs",      # Format file systems
            r";.*?;",     # Command chaining that might be suspicious
            r">\s*/dev/", # Redirecting to devices
            r">\s*/etc/"  # Redirecting to system configuration
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                logging.warning(f"Blocked command matching dangerous pattern: {command}")
                return False
        
        return True