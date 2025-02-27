import sys
import logging
import traceback

class ErrorHandler:
    """
    Global error handler for the AI Assistant application.
    Provides centralized error handling, logging, and recovery mechanisms.
    """
    
    @staticmethod
    def setup_exception_handler():
        """
        Set up global exception handler for unhandled exceptions.
        """
        def handle_exception(exc_type, exc_value, exc_traceback):
            # Log the error
            logging.error("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))
            
            # Print to stderr
            print("An unexpected error occurred:", file=sys.stderr)
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
        
        # Set the exception handler
        sys.excepthook = handle_exception
    
    @staticmethod
    def try_except(func, error_message="An error occurred", default_return=None):
        """
        Function wrapper for try-except pattern.
        
        :param func: Function to execute
        :param error_message: Message to log on error
        :param default_return: Value to return on error
        :return: Function result or default_return on error
        """
        try:
            return func()
        except Exception as e:
            logging.error(f"{error_message}: {str(e)}")
            return default_return
    
    @staticmethod
    def validate_input(input_data, input_type=None):
        """
        Validate input data.
        
        :param input_data: Data to validate
        :param input_type: Expected type
        :return: (is_valid, message)
        """
        if input_data is None:
            return False, "Input data is None"
        
        if input_type and not isinstance(input_data, input_type):
            return False, f"Expected {input_type.__name__}, got {type(input_data).__name__}"
        
        return True, "Input is valid"