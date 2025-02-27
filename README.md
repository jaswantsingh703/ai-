# AI Assistant Project 🚀

## Overview

This AI Assistant is a **multi-functional, self-improving** system powered by **Llama3, GPT4All, Whisper, BabyAGI**, and automation tools. It includes **voice recognition, web browsing, AI-generated task execution, image/video processing, and system control**.

## Features

✔ **AI Model Integration** - Supports GPT4All, Llama3, Whisper.
✔ **Voice Processing** - Speech recognition and text-to-speech.
✔ **Web Browsing & AI Auto-Learning** - Internet search and self-improvement.
✔ **Task Execution** - Uses BabyAGI for intelligent task automation.
✔ **System Automation** - Controls Windows, Mac, and Linux commands.
✔ **Image & Video Processing** - AI-powered recognition and processing.
✔ **Self-Improvement & Auto-Development** - AI that evolves over time.
✔ **Database & Memory Storage** - User interaction history with MongoDB.

## Installation

### Prerequisites:

- **Python 3.10+**
- **pip** installed
- **Virtual environment (recommended)**

### Setup:

```bash
# Clone the repository
git clone https://github.com/your-repo/ai-assistant.git
cd ai-assistant

# Create a virtual environment
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run the AI Assistant

```bash
python main.py
```

### Train AI on Custom Data

```bash
python src/training/train_model.py --data data/
```

### Automate System Tasks

```bash
python src/platform_integration/system_control.py --task "Open Chrome"
```

## File Structure

```
AI_Project/
│── main.py                           # Main AI Assistant Script
│── requirements.txt                   # Dependencies
│── README.md                          # Project Documentation
│── logs/                              # Logs Folder
│── src/                               # Source Code Directory
│   ├── ai_core/                        # AI Core Modules
│   ├── gui/                            # Graphical User Interface
│   ├── platform_integration/           # System Control
│   ├── task_management/                # AI Task Execution
│   ├── training/                        # AI Model Training
│   ├── database/                        # User Data Storage
│── data/                               # Data for Training
│── models/                             # AI Model Checkpoints
│── test/                               # Unit Tests
│── scripts/                            # Additional Scripts
```

## Contributing

Pull requests are welcome! Make sure to open an issue before making major changes.

## License

MIT License © 2025 AI Assistant Team
