#!/bin/bash

# Deployment script for AI Assistant

# Stop on any error
set -e

# Define project variables
PROJECT_NAME="AI_Assistant"
VENV_DIR="venv"
DEPLOY_DIR="/var/www/$PROJECT_NAME"
LOG_DIR="$DEPLOY_DIR/logs"

# Parse command line arguments
while getopts ":d:" opt; do
  case $opt in
    d) DEPLOY_DIR="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    exit 1
    ;;
  esac
done

echo "Deploying $PROJECT_NAME to $DEPLOY_DIR"

# Check if we have sudo rights
if [[ $(id -u) -ne 0 ]]; then
    echo "⚠️ Warning: You're not running as root, some operations may fail."
fi

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# Update dependencies
echo "Updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p $DEPLOY_DIR
mkdir -p $LOG_DIR
mkdir -p $DEPLOY_DIR/models
mkdir -p $DEPLOY_DIR/data

# Copy application files
echo "Copying application files..."
rsync -av --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' ./ $DEPLOY_DIR/

# Set permissions
echo "Setting permissions..."
chmod -R 755 $DEPLOY_DIR

# Create service file for systemd
SERVICE_FILE="/etc/systemd/system/ai_assistant.service"
if [[ $(id -u) -eq 0 ]]; then
    echo "Creating systemd service..."
    cat > $SERVICE_FILE << EOF
[Unit]
Description=AI Assistant Service
After=network.target

[Service]
User=www-data
WorkingDirectory=$DEPLOY_DIR
ExecStart=$DEPLOY_DIR/$VENV_DIR/bin/python $DEPLOY_DIR/main.py --mode cli
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=ai_assistant

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable ai_assistant.service
    
    # Restart application service
    echo "Restarting application..."
    systemctl restart ai_assistant.service
else
    echo "⚠️ Warning: Not running as root, skipping service creation."
fi

# Display success message
echo "✅ Deployment completed successfully."
echo "To start the application, run: systemctl start ai_assistant"
echo "To check status, run: systemctl status ai_assistant"