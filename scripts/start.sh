#!/bin/bash

# Start script for AI Assistant

# Stop on any error
set -e

# Define project variables
PROJECT_NAME="AI_Assistant"
VENV_DIR="venv"
LOG_DIR="logs"
MAIN_SCRIPT="main.py"

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Ensure dependencies are installed
pip install --upgrade pip
pip install -r requirements.txt

# Start the AI Assistant
echo "Starting AI Assistant..."
nohup python $MAIN_SCRIPT > $LOG_DIR/ai_assistant.log 2>&1 &

echo "AI Assistant is running in the background. Logs available at $LOG_DIR/ai_assistant.log"
