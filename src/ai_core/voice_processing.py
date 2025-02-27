import os
import logging
import tempfile
import threading
import time
import numpy as np
import wave
import pyttsx3
from src.utils.config import Config

# Check if required modules are available
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logging.warning("speech_recognition module not available. Using fallback methods.")

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logging.warning("sounddevice module not available.")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("whisper module not available.")

class VoiceAssistant:
    """
    Voice Assistant with speech recognition and text-to-speech capabilities.
    Uses multiple fallback methods for robustness.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the Voice Assistant with fallback options.
        """
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            logging.info("TTS engine initialized")
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {e}")
            self.tts_engine = None
        
        # Initialize speech recognition if available
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            logging.info("Speech recognition initialized")
        else:
            self.recognizer = None
        
        # Try to initialize Whisper for better transcription
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                logging.info("Whisper model initialized")
            except Exception as e:
                logging.error(f"Failed to initialize Whisper model: {e}")
        
        # Recording parameters
        self.sample_rate = 16000
        self.is_listening = False
        self.model_path = model_path or Config.get("default_model_path")
    
    def listen(self, timeout=5, phrase_time_limit=None):
        """
        Capture voice input from the microphone with improved error handling.
        
        Args:
            timeout (int): Seconds to wait before timing out
            phrase_time_limit (int, optional): Maximum seconds to record
            
        Returns:
            str: Transcribed text or error message
        """
        # Prevent multiple listening sessions
        if self.is_listening:
            return "Already listening to another request."
        
        self.is_listening = True
        
        try:
            # Try using speech_recognition if available
            if SPEECH_RECOGNITION_AVAILABLE and self.recognizer:
                return self._listen_with_sr(timeout, phrase_time_limit)
            elif SOUNDDEVICE_AVAILABLE:
                # Fallback to manual recording
                return self._listen_with_sounddevice(timeout)
            else:
                logging.error("No voice input method available")
                return "Voice input is not available. Please install required packages."
        finally:
            self.is_listening = False
    
    def _listen_with_sr(self, timeout, phrase_time_limit):
        """
        Listen using the speech_recognition library.
        """
        with sr.Microphone() as source:
            print("🎤 Listening...")
            
            try:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                print("🔊 Processing audio...")
                
                # Try multiple recognition methods
                text = self._transcribe_audio(audio)
                
                if text:
                    return text
                else:
                    return ""
                    
            except sr.WaitTimeoutError:
                print("⌛ Listening timed out.")
                return ""
                
            except Exception as e:
                logging.error(f"Error in speech recognition: {e}")
                return ""
    
    def _listen_with_sounddevice(self, duration=5):
        """
        Listen using sounddevice as a fallback.
        """
        print("🎤 Recording...")
        
        try:
            # Record audio
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1
            )
            sd.wait()
            
            print("🔊 Processing audio...")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_path = temp_file.name
                
            self._save_wav(temp_path, recording, self.sample_rate)
            
            # Transcribe with Whisper if available
            if self.whisper_model:
                result = self.whisper_model.transcribe(temp_path)
                text = result["text"]
            else:
                text = ""
                logging.warning("No transcription model available.")
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
            return text
            
        except Exception as e:
            logging.error(f"Error recording audio: {e}")
            return ""
    
    def _transcribe_audio(self, audio):
        """
        Try multiple methods to transcribe audio.
        """
        # Try Whisper first (more accurate)
        if self.whisper_model:
            try:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_path = temp_file.name
                    temp_file.write(audio.get_wav_data())
                
                # Transcribe
                result = self.whisper_model.transcribe(temp_path)
                
                # Clean up
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
                return result["text"]
                
            except Exception as e:
                logging.error(f"Whisper transcription error: {e}")
                # Continue to fallback methods
        
        # Try Google (fallback)
        if SPEECH_RECOGNITION_AVAILABLE and self.recognizer:
            try:
                return self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                logging.warning("Google could not understand audio")
            except sr.RequestError as e:
                logging.error(f"Google request error: {e}")
        
        return ""
    
    def _save_wav(self, file_path, audio_data, sample_rate):
        """
        Save audio data as a WAV file.
        """
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
    
    def speak(self, text):
        """
        Convert text to speech with error handling.
        
        Args:
            text (str): Text to speak
            
        Returns:
            bool: Success status
        """
        if not text:
            return False
            
        if not self.tts_engine:
            logging.error("TTS engine not available")
            return False
            
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logging.error(f"Error in text-to-speech: {e}")
            return False
    
    def process_voice_command(self):
        """
        Listen to a voice command and prepare response.
        
        Returns:
            str: Recognized command or empty string
        """
        command = self.listen()
        
        if command:
            print(f"🎙️ You said: {command}")
            return command
            
        return