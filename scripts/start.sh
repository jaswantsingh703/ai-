#!/bin/bash

# Start script for AI Assistant

# Stop on any error
set -e

# Define project variables
PROJECT_NAME="AI_Assistant"
VENV_DIR="venv"
LOG_DIR="logs"
MAIN_SCRIPT="main.py"
MODE="gui"  # Default mode

# Parse command line arguments
while getopts ":m:" opt; do
  case $opt in
    m) MODE="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
       echo "Usage: ./start.sh [-m mode]"
       echo "Modes: cli, voice, gui, automation"
       exit 1
    ;;
  esac
done

echo "Starting AI Assistant in $MODE mode..."

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Ensure dependencies are installed
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Check if config.yaml exists, create if not
if [ ! -f "config.yaml" ]; then
    echo "Creating default configuration..."
    cat > config.yaml << EOF
# General Settings
project_name: "AI Assistant"
version: "1.0.0"
debug_mode: true

# Paths
data_dir: "data"
logs_dir: "logs"
models_dir: "models"

# Model Configuration
default_model_type: "gpt4all"
default_model_path: "models/gpt4all-j-v1.3-groovy.bin"
fallback_model_type: "gpt4all"

# Security Settings
enable_system_control: false
EOF
fi

# Start the AI Assistant
echo "Starting AI Assistant..."
if [ "$MODE" == "gui" ]; then
    # Run in foreground for GUI mode
    python $MAIN_SCRIPT --mode $MODE
else
    # Run in background for other modes
    nohup python $MAIN_SCRIPT --mode $MODE > $LOG_DIR/ai_assistant.log 2>&1 &
    echo "AI Assistant is running in the background. Logs available at $LOG_DIR/ai_assistant.log"
    echo "To view logs in real-time, run: tail -f $LOG_DIR/ai_assistant.log"
fi