import torch
import logging
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import gpt4all
import whisper
from src.utils.config import Config

class AIModel:
    """
    AI Model integration with improved error handling and fallback mechanisms.
    Supports Llama3, GPT4All, and Whisper for voice processing.
    """
    
    def __init__(self, model_type=None, model_path=None):
        """
        Initialize AI Model based on the selected type.
        
        Args:
            model_type (str): Model type - "llama3", "gpt4all", or "whisper"
            model_path (str): Path to model file for local models
        """
        # Use config if parameters not provided
        self.model_type = model_type or Config.get("default_model_type", "gpt4all")
        self.model_path = model_path or Config.get("default_model_path")
        
        self.model = None
        self.tokenizer = None
        self.is_fallback = False
        
        # Ensure models directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        try:
            logging.info(f"Initializing {self.model_type} model")
            
            if self.model_type == "llama3":
                try:
                    # Try to load Llama3 model
                    self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3-8B")
                    self.model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3-8B")
                    logging.info("Llama3 model loaded successfully")
                except Exception as e:
                    logging.error(f"Failed to load Llama3 model: {e}")
                    # Fallback to GPT4All
                    logging.info("Falling back to GPT4All model")
                    self.model_type = "gpt4all"
                    self.model = gpt4all.GPT4All()
                    self.is_fallback = True
                    
            elif self.model_type == "gpt4all":
                try:
                    # Check if model file exists
                    if os.path.exists(self.model_path):
                        self.model = gpt4all.GPT4All(self.model_path)
                    else:
                        logging.warning(f"Model file not found: {self.model_path}")
                        logging.info("Using default GPT4All model")
                        self.model = gpt4all.GPT4All()
                        
                    logging.info("GPT4All model loaded successfully")
                except Exception as e:
                    logging.error(f"Failed to load GPT4All model: {e}")
                    self.is_fallback = True
                    
            elif self.model_type == "whisper":
                try:
                    self.model = whisper.load_model("base")
                    logging.info("Whisper model loaded successfully")
                except Exception as e:
                    logging.error(f"Failed to load Whisper model: {e}")
                    self.is_fallback = True
            else:
                logging.error(f"Unsupported model type: {self.model_type}")
                self.is_fallback = True
                
        except Exception as e:
            logging.error(f"Error initializing model: {e}")
            self.is_fallback = True
    
    def generate_response(self, input_text):
        """
        Generate AI response for text input.
        
        Args:
            input_text (str): User input text
            
        Returns:
            str: AI-generated response
        """
        if not input_text or not input_text.strip():
            return "I need some input to generate a response."
        
        try:
            if self.is_fallback:
                # Simple response for fallback mode
                return self._generate_fallback_response(input_text)
                
            if self.model_type == "llama3" and self.model and self.tokenizer:
                inputs = self.tokenizer(input_text, return_tensors="pt")
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs, 
                        max_length=150, 
                        num_return_sequences=1,
                        temperature=0.7
                    )
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            elif self.model_type == "gpt4all" and self.model:
                return self.model.generate(input_text, max_tokens=200)
                
            else:
                return "I'm having trouble generating a response with the current model configuration."
                
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"I encountered an error while processing your request. Please try again or contact support."
    
    def _generate_fallback_response(self, input_text):
        """
        Generate a simple rule-based response when models are unavailable.
        
        Args:
            input_text (str): User input text
            
        Returns:
            str: Simple response
        """
        input_lower = input_text.lower()
        
        # Simple rule-based responses
        if any(greeting in input_lower for greeting in ["hello", "hi", "hey"]):
            return "Hello! I'm currently operating in basic mode. How can I help you?"
            
        elif "how are you" in input_lower:
            return "I'm functioning in basic mode, but ready to assist you as best I can."
            
        elif any(word in input_lower for word in ["thanks", "thank you"]):
            return "You're welcome! Let me know if you need anything else."
            
        elif "help" in input_lower or "?" in input_text:
            return "I can try to help you, but I'm currently in basic mode with limited capabilities."
            
        else:
            # Generic response for other queries
            return (
                "I understand you're asking about: " + input_text + 
                "\n\nI'm currently operating in basic mode with limited functionality. " +
                "For more advanced responses, please check that the AI models are properly configured."
            )
    
    def transcribe_audio(self, audio_path):
        """
        Transcribe audio input using Whisper model.
        
        Args:
            audio_path (str): Path to audio file
            
        Returns:
            str: Transcribed text
        """
        if not os.path.exists(audio_path):
            return "Audio file not found."
            
        try:
            if self.model_type == "whisper" and self.model:
                result = self.model.transcribe(audio_path)
                return result["text"]
            else:
                # Try to initialize whisper model for transcription
                try:
                    whisper_model = whisper.load_model("base")
                    result = whisper_model.transcribe(audio_path)
                    return result["text"]
                except Exception as e:
                    logging.error(f"Error loading temporary Whisper model: {e}")
                    return "Audio transcription is only available with Whisper model."
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return "Failed to transcribe audio. Please try again or check the file format."
    
    def process_file_input(self, file_path):
        """
        Process a text file and return AI-generated summary.
        
        Args:
            file_path (str): Path to text file
            
        Returns:
            str: AI-generated summary
        """
        if not os.path.exists(file_path):
            return "File not found."
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                return self.generate_response(f"Summarize this content: {content}")
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            return f"Error processing file: {str(e)}"
    
    def change_model(self, new_model_type, new_model_path=None):
        """
        Change the current model to a different type.
        
        Args:
            new_model_type (str): New model type
            new_model_path (str, optional): New model path
            
        Returns:
            bool: Success status
        """
        try:
            # Initialize with new parameters
            new_model = AIModel(
                model_type=new_model_type, 
                model_path=new_model_path or self.model_path
            )
            
            # If successful, update self
            self.model_type = new_model.model_type
            self.model = new_model.model
            self.tokenizer = new_model.tokenizer
            self.is_fallback = new_model.is_fallback
            
            logging.info(f"Model changed to {new_model_type}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to change model: {e}")
            return False