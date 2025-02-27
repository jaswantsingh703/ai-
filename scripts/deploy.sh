#!/bin/bash

# Deployment script for AI Assistant

# Stop on any error
set -e

# Define project variables
PROJECT_NAME="AI_Assistant"
VENV_DIR="venv"
DEPLOY_DIR="/var/www/$PROJECT_NAME"
LOG_DIR="$DEPLOY_DIR/logs"

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p $LOG_DIR

# Apply database migrations (if applicable)
if [ -f "manage.py" ]; then
    echo "Applying database migrations..."
    python manage.py migrate
fi

# Restart application service
echo "Restarting application..."
systemctl restart ai_assistant.service

# Display success message
echo "Deployment completed successfully."
