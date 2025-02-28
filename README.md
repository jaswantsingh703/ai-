# Jarvis AI Assistant 🤖

A complete AI assistant project that integrates GPT4All, Llama 3, Whisper, BabyAGI, and other cutting-edge AI technologies into a powerful, voice-controlled assistant that works on macOS, Windows, and Linux.

## 🌟 Features

- **Multiple AI Models**: Integrates GPT4All, Llama 3, and Whisper for different AI tasks
- **Voice Control**: Responds to voice commands in both Hindi and English
- **Dual Interface**: Offers both GUI and CLI modes
- **System Automation**: Controls applications, changes volume, and more
- **Web Browsing**: Searches the web and summarizes content
- **Computer Vision**: Processes images and videos for face detection and OCR
- **Self-Learning**: Remembers past interactions using ChromaDB
- **Task Automation**: Uses BabyAGI for autonomous task planning and execution
- **Self-Improvement**: Generates new code and tools dynamically

## 🛠️ Installation

### Prerequisites

For macOS M1:

```bash
# Install required system libraries
brew install cmake
brew install portaudio
brew install ffmpeg
brew install tesseract
brew install opencv
```

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/jarvis-ai.git
cd jarvis-ai
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Download AI models:

- Place Whisper model (`whisper-medium.pt`) in `models/`
- Place Llama model (`llama-7b.ggmlv3.q4_0.bin`) in `models/`
- Place GPT4All model (`gpt4all-falcon-q4_0.bin`) in `models/`

5. Configure API keys:

- Copy the `.env.example` file to `.env` and fill in your API keys

## 🚀 Usage

### Start the AI Assistant

Run in GUI mode (default):

```bash
python main.py
```

Run in CLI mode:

```bash
python main.py --mode cli
```

Run in voice mode:

```bash
python main.py --mode voice
```

Run in automation mode:

```bash
python main.py --mode automation
```

### Example Commands

- "Jarvis, open Chrome"
- "Jarvis, what's the latest AI news?"
- "Jarvis, run a port scan"
- "Jarvis, detect faces in sample_image.png"
- "Jarvis, extract text from document.png"
- "Jarvis, improve yourself by creating a tool for weather forecasting"
- "Jarvis, add task: research new machine learning papers"
- "Jarvis, show tasks"

## 📁 Project Structure

```
AI_Project/
├── main.py                           # Main entry point
├── requirements.txt                  # All dependencies
├── README.md                         # Project documentation
├── logs/                             # Log files
│   ├── ai_logs.log
│   └── error_logs.log
├── src/                              # Source code directory
│    ├── ai_core/                     # Core AI modules
│    │    ├── model_integration.py    # GPT4All, Llama 3, Whisper integration
│    │    ├── voice_processing.py     # Voice recognition and TTS
│    │    ├── web_browsing.py         # Web search and scraping
│    │    ├── image_processing.py     # OCR and face detection
│    │    ├── video_processing.py     # Video analysis
│    │    ├── self_improvement.py     # Auto-code-generation
│    │    └── real_time_learning.py   # Memory with ChromaDB
│    ├── gui/                         # GUI modules
│    │    ├── main_window.py          # Main PyQt5 GUI window
│    │    └── voice_gui.py            # Voice-enabled GUI interface
│    ├── platform_integration/        # OS-specific automation
│    │    ├── system_control.py       # Generic system control
│    │    ├── mac_automation.py       # macOS automation
│    │    ├── windows_automation.py   # Windows automation
│    │    └── linux_automation.py     # Linux automation
│    ├── task_management/             # Task scheduling and execution
│    │    ├── babyagi_agent.py        # BabyAGI integration
│    │    └── task_scheduler.py       # Task scheduler
│    ├── database/                    # User data storage
│    │    └── user_data.py            # User data management
│    ├── security/                    # Security modules
│    │    └── ai_security.py          # Input validation and filtering
│    ├── training/                    # AI model training
│    │    ├── train_model.py          # Model training
│    │    └── dataset_loader.py       # Dataset loading utilities
│    └── utils/                       # Utility functions
│         ├── config.py               # Global configuration
│         ├── error_handler.py        # Error handling
│         └── helper_functions.py     # Helper utilities
├── data/                             # Training data
├── models/                           # Model checkpoint files
├── test/                             # Unit tests
│    ├── test_ai_core.py
│    ├── test_gui.py
│    └── test_voice.py
└── scripts/                          # Deployment scripts
     ├── deploy.sh                    # Deployment script
     └── start.sh                     # Start script
```

## 🔧 Configuration

The project uses a combination of `config.yaml` and `.env` files for configuration:

### config.yaml

```yaml
# General Settings
project_name: "Jarvis AI"
version: "1.0.0"
debug_mode: true

# Paths
data_dir: "data"
logs_dir: "logs"
models_dir: "models"

# Model Configuration
default_model_type: "gpt4all"
default_model_path: "models/gpt4all-j-v1.3-groovy.bin"
```

### .env

```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here
```

## 🧠 AI Models

### GPT4All

- Used for general text generation and conversation
- Lightweight and can run locally without an internet connection
- Default model for most tasks

### Llama 3

- More powerful model for complex reasoning tasks
- Better context understanding and generation
- Used when higher quality output is needed

### Whisper

- State-of-the-art speech recognition model
- Provides accurate voice-to-text conversion
- Supports multiple languages including Hindi and English

## 🤖 BabyAGI Integration

The BabyAGI agent provides autonomous task planning and execution:

1. Create tasks with: "Jarvis, add task: [description]"
2. View tasks with: "Jarvis, show tasks"
3. Run tasks with: "Jarvis, run tasks"

The agent can:

- Break down complex goals into manageable tasks
- Learn from previous executions to improve future plans
- Store context in memory for improved performance

## 🔍 Hacking Lab Features

For educational purposes only, the project includes basic cybersecurity features:

- Port scanning: "Jarvis, run a port scan on [ip]"
- Ping sweep: "Jarvis, run a ping sweep on [subnet]"

⚠️ **Warning**: Only use these features on systems you own or have permission to test.

## 🖥️ GUI

The GUI interface provides:

- Text input and display area
- Voice command button
- History of interactions
- File selection dialog for image/video processing

## 🎤 Voice Control

Voice commands follow this pattern:

- Start with "Jarvis" (wake word)
- Continue with a command ("open", "search", "run", etc.)
- End with required parameters

Example: "Jarvis, search for the latest AI developments"

## 🧪 Testing

Run the unit tests to ensure everything is working correctly:

```bash
python -m unittest discover test
```

## 🔧 Troubleshooting

### Common Issues

1. **Model loading errors**:

   - Ensure model files are in the correct location
   - Check file permissions

2. **Voice recognition not working**:

   - Install required audio libraries
   - Check microphone permissions

3. **GUI not displaying**:
   - Ensure PyQt5 is installed correctly
   - Install additional dependencies if needed

## 📚 Documentation

- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/dev_guide.md)
- [Architecture](docs/architecture.md)

## 🛡️ Security

This project implements several security measures:

- Input validation to prevent command injection
- Response filtering to prevent sensitive data leakage
- Command restrictions to prevent system damage
- Logging of security events

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- OpenAI for the Whisper model
- Meta AI for the Llama model
- The GPT4All team
- The PyQt team
- All contributors and testers
