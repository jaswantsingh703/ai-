import logging
import re
from src.utils.config import Config

class AISecurity:
    """
    Security and content filtering module for the AI assistant.
    Provides input validation, output filtering, and security checks.
    """
    
    def __init__(self):
        """Initialize the AI Security module."""
        # Restricted keywords for dangerous content
        self.restricted_keywords = [
            # System commands
            "rm -rf", "format", "del /", "mkfs", "sudo rm", 
            "chmod 777", "dd if", ":(){ :|:& };:", "> /dev/sda",
            # Destructive actions
            "wipe", "destroy", "erase all", "delete system",
            # Malicious intent
            "hack password", "hack account", "steal credentials",
            "bypass security", "crack password", "exploit vulnerability"
        ]
        
        # Sensitive phrases to check in AI responses
        self.sensitive_phrases = [
            "sudo password", "root password", "api key", "secret key",
            "access token", "private key", "ssh key", "encryption key",
            "auth token", "authorization token", "database password"
        ]
        
        # Dangerous command patterns
        self.dangerous_patterns = [
            # System destructive commands
            r"rm\s+-rf\s+[\/\*]",
            r"mkfs\.[a-z]+\s+\/dev\/[a-z]+",
            r"dd\s+if=.*\s+of=\/dev\/[a-z]+",
            r"format\s+[a-z]\:",
            r"del\s+\/[a-z]\s+\/[a-z]\s+",
            # Privilege escalation
            r"sudo\s+su",
            r"sudo\s+\-i",
            # Shell command execution
            r"eval\(.*\)",
            r"exec\(.*\)",
            r"os\.system\(.*\)",
            r"subprocess\..*\(.*\)",
            # Network attacks
            r"nmap\s+\-[a-z]*p",
            r"ping\s+\-f",
            # Recursive payloads
            r":\(\)\s*\{\s*:\|:",
            # Web attacks
            r"curl.+\|\s*bash",
            r"wget.+\|\s*bash"
        ]
        
        # Load additional items from config
        config_restricted = Config.get("security_restricted_keywords", [])
        if config_restricted:
            self.restricted_keywords.extend(config_restricted)
        
        logging.info("AI Security module initialized")
    
    def validate_input(self, user_input):
        """
        Validate user input for security issues.
        
        Args:
            user_input (str): User input to validate
            
        Returns:
            tuple: (is_valid, filtered_input_or_error_message)
        """
        if not user_input:
            return True, ""
        
        # Check for restricted keywords
        for keyword in self.restricted_keywords:
            if keyword.lower() in user_input.lower():
                logging.warning(f"Blocked input containing restricted keyword: {keyword}")
                return False, "I cannot process this command for security reasons."
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                logging.warning(f"Blocked input matching dangerous pattern: {pattern}")
                return False, "This command contains potentially harmful patterns."
        
        # Check string length
        if len(user_input) > 1000:
            logging.warning(f"Input too long: {len(user_input)} characters")
            return False, "Your input is too long. Please keep it under 1000 characters."
        
        return True, user_input
    
    def filter_response(self, response):
        """
        Filter AI responses to remove potentially sensitive information.
        
        Args:
            response (str): AI response to filter
            
        Returns:
            str: Filtered response
        """
        if not response:
            return ""
        
        filtered_response = response
        
        # Check for sensitive information patterns
        for phrase in self.sensitive_phrases:
            # Check if the phrase is in the response
            if phrase.lower() in filtered_response.lower():
                # Find the sensitive context and redact it
                pattern = fr'({phrase}\s*[=:]\s*[\w\.\-\+\/]+)'
                filtered_response = re.sub(
                    pattern, 
                    f"{phrase}: [REDACTED]", 
                    filtered_response, 
                    flags=re.IGNORECASE
                )
                
                logging.warning(f"Filtered sensitive information from response: {phrase}")
        
        # Check for IP addresses and consider redacting some
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_addresses = re.findall(ip_pattern, filtered_response)
        for ip in ip_addresses:
            # Don't redact localhost or common private IPs
            if ip not in ["127.0.0.1", "192.168.1.1", "10.0.0.1", "172.16.0.1"]:
                # Redact the last octet
                parts = ip.split('.')
                parts[-1] = "xxx"
                redacted_ip = '.'.join(parts)
                filtered_response = filtered_response.replace(ip, redacted_ip)
        
        # Max response length check
        max_length = Config.get("max_response_length", 5000)
        if len(filtered_response) > max_length:
            filtered_response = filtered_response[:max_length] + "... [Response truncated due to length]"
            logging.warning(f"Response truncated due to length: {len(response)} characters")
        
        return filtered_response
    
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
        
        # Check if system control is enabled in config
        if not Config.get("enable_system_control", False):
            logging.warning("System control is disabled, blocking command execution")
            return False
        
        # Get allowed commands from config
        allowed_commands = Config.get("allowed_commands", [])
        
        # Extract base command (first word)
        base_command = command.split()[0].lower()
        
        # Check if command is in allowed list
        if base_command not in allowed_commands:
            logging.warning(f"Command not in allowed list: {base_command}")
            return False
        
        # Check for restricted keywords and patterns
        for keyword in self.restricted_keywords:
            if keyword.lower() in command.lower():
                logging.warning(f"Command contains restricted keyword: {keyword}")
                return False
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                logging.warning(f"Command matches dangerous pattern: {pattern}")
                return False
        
        return True
    
    def sanitize_filename(self, filename):
        """
        Sanitize a filename to prevent path traversal and command injection.
        
        Args:
            filename (str): Filename to sanitize
            
        Returns:
            str: Sanitized filename
        """
        if not filename:
            return "unnamed_file"
        
        # Remove path traversal characters
        sanitized = re.sub(r'[\/\\\.\.]', '', filename)
        
        # Remove any non-alphanumeric or safe characters
        sanitized = re.sub(r'[^\w\-\.]', '_', sanitized)
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            return "unnamed_file"
        
        return sanitized