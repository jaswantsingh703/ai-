import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import gpt4all
import whisper
import os

class AIModel:
    def __init__(self, model_type="llama3", model_path="models/llama-7b.ggmlv3.q4_0.bin"):
        """
        Initialize AI Model based on the selected type.
        Supports Llama3, GPT4All, and Whisper for voice processing.
        """
        self.model_type = model_type
        self.model_path = model_path
        
        if model_type == "llama3":
            self.tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
            self.model = AutoModelForCausalLM.from_pretrained("meta-llama/Meta-Llama-3-8B")
        elif model_type == "gpt4all":
            self.model = gpt4all.GPT4All(model_path)
        elif model_type == "whisper":
            self.model = whisper.load_model("medium")
        else:
            raise ValueError("Unsupported model type. Choose from 'llama3', 'gpt4all', or 'whisper'.")

    def generate_response(self, input_text):
        """
        Generate AI response for text input.
        """
        if self.model_type == "llama3":
            inputs = self.tokenizer(input_text, return_tensors="pt")
            outputs = self.model.generate(**inputs, max_length=150)
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        elif self.model_type == "gpt4all":
            return self.model.generate(input_text)
        else:
            raise ValueError("Unsupported model type for text response.")

    def transcribe_audio(self, audio_path):
        """
        Transcribe audio input using Whisper model.
        """
        if self.model_type == "whisper":
            return self.model.transcribe(audio_path)["text"]
        else:
            raise ValueError("Audio transcription is only available with Whisper model.")

    def process_file_input(self, file_path):
        """
        Process a text file and return AI-generated summary.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found.")
        
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            return self.generate_response(f"Summarize this content: {content}")

# Example Usage
if __name__ == "__main__":
    ai_model = AIModel(model_type="llama3")
    response = ai_model.generate_response("What is AI?")
    print("AI Response:", response)