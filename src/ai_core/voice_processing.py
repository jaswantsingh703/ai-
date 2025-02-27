import speech_recognition as sr
import pyttsx3
import whisper
import os

class VoiceAssistant:
    def __init__(self, model_path="models/whisper-medium.pt"):
        """
        Initialize the Voice Assistant with Whisper model for speech recognition and pyttsx3 for TTS.
        """
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.model = whisper.load_model("medium")
        self.model_path = model_path

    def listen(self):
        """
        Capture voice input from the microphone and transcribe it using Whisper.
        """
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        
        try:
            # Save audio to temporary file
            temp_audio_path = "temp_audio.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio.get_wav_data())
            
            # Transcribe using Whisper
            transcription = self.model.transcribe(temp_audio_path)["text"]
            os.remove(temp_audio_path)  # Clean up temp file
            return transcription
        except Exception as e:
            print("❌ Error recognizing speech:", e)
            return ""

    def speak(self, text):
        """
        Convert text to speech using pyttsx3.
        """
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def process_voice_command(self):
        """
        Listen to a voice command and respond accordingly.
        """
        command = self.listen()
        if command:
            print("🎙️ You said:", command)
            response = f"Processing command: {command}"
            self.speak(response)
            return command
        return None

# Example Usage
if __name__ == "__main__":
    assistant = VoiceAssistant()
    command = assistant.process_voice_command()
    if command:
        print("✅ Command Processed:", command)
