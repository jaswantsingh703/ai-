#!/bin/bash

# Jarvis AI Assistant Setup Script
# This script automates the setup of Jarvis AI on MacOS, Linux, or Windows (with WSL)

set -e  # Exit immediately if a command exits with a non-zero status

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "    __                  _         _    ___ "
echo "    \ \  __ _ _ ____   (_)___    / \  |_ _|"
echo "     \ \/ _\` | '__\ \ / / / __|  / _ \  | | "
echo "  /\_/ / (_| | |   \ V /| \__ \ / ___ \ | | "
echo "  \___/ \__,_|_|    \_/ |_|___//_/   \_\___|"
echo -e "${NC}"
echo "  Setting up Jarvis AI Assistant..."
echo ""

# Detect OS
DETECTED_OS=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    DETECTED_OS="macos"
    echo -e "${GREEN}Detected MacOS${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DETECTED_OS="linux"
    echo -e "${GREEN}Detected Linux${NC}"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    DETECTED_OS="windows"
    echo -e "${YELLOW}Detected Windows. This script is designed for WSL or Git Bash.${NC}"
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

# Function to ask yes/no question
ask() {
    local prompt default reply
    prompt="${1}"
    default="${2}"
    
    if [ "${default}" = "Y" ]; then
        prompt="${prompt} [Y/n] "
    elif [ "${default}" = "N" ]; then
        prompt="${prompt} [y/N] "
    else
        prompt="${prompt} [y/n] "
    fi
    
    while true; do
        read -p "$prompt" reply
        if [ -z "$reply" ]; then
            reply=$default
        fi
        
        case "$reply" in
            [Yy]*) return 0 ;;
            [Nn]*) return 1 ;;
            *) echo -e "${RED}Please answer yes or no.${NC}" ;;
        esac
    done
}

# Function to check command availability
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# Create a Python virtual environment
setup_virtual_env() {
    echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
    
    # Check if Python is installed
    if ! check_command python3; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    else
        echo "Virtual environment already exists."
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Verify activation
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${RED}Failed to activate virtual environment.${NC}"
        exit 1
    else
        echo -e "${GREEN}Virtual environment activated successfully.${NC}"
    fi
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
}

# Install system dependencies
install_system_dependencies() {
    echo -e "\n${BLUE}Installing system dependencies...${NC}"
    
    if [ "$DETECTED_OS" = "macos" ]; then
        # Check if Homebrew is installed
        if ! check_command brew; then
            echo -e "${YELLOW}Homebrew is not installed. Installing Homebrew...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install dependencies with Homebrew
        echo "Installing dependencies with Homebrew..."
        brew install cmake portaudio ffmpeg tesseract opencv python
        
    elif [ "$DETECTED_OS" = "linux" ]; then
        # Detect Linux distribution
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            DISTRO=$ID
            
            case $DISTRO in
                ubuntu|debian)
                    echo "Installing dependencies for Ubuntu/Debian..."
                    sudo apt-get update
                    sudo apt-get install -y build-essential cmake libportaudio2 libportaudiocpp0 portaudio19-dev ffmpeg tesseract-ocr libopencv-dev python3-dev python3-tk
                    ;;
                fedora)
                    echo "Installing dependencies for Fedora..."
                    sudo dnf install -y cmake portaudio-devel ffmpeg tesseract opencv-devel python3-devel python3-tkinter
                    ;;
                *)
                    echo -e "${YELLOW}Unsupported Linux distribution: $DISTRO. You may need to install dependencies manually.${NC}"
                    ;;
            esac
        else
            echo -e "${YELLOW}Unable to determine Linux distribution. You may need to install dependencies manually.${NC}"
        fi
    elif [ "$DETECTED_OS" = "windows" ]; then
        echo -e "${YELLOW}On Windows, please ensure you have the following installed:${NC}"
        echo "  - Visual C++ Build Tools"
        echo "  - CMake"
        echo "  - Python 3.8 or higher with development headers"
        echo ""
        echo "You may install Python packages through pip, but system libraries must be installed manually."
    fi
}

# Install Python dependencies
install_python_dependencies() {
    echo -e "\n${BLUE}Installing Python dependencies...${NC}"
    
    # Install required packages
    pip install -r requirements.txt
    
    # Verify key packages
    echo "Verifying key packages..."
    python -c "import torch; print(f'PyTorch: {torch.__version__}')"
    python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
    
    echo -e "${GREEN}Python dependencies installed successfully.${NC}"
}

# Download AI models
download_models() {
    echo -e "\n${BLUE}Setting up AI models...${NC}"
    
    # Create models directory
    mkdir -p models
    
    # Function to download a model if not exists
    download_if_not_exists() {
        local url=$1
        local output_path=$2
        local description=$3
        
        if [ ! -f "$output_path" ]; then
            echo "Downloading $description..."
            curl -L "$url" -o "$output_path"
            echo -e "${GREEN}Downloaded $description to $output_path${NC}"
        else
            echo -e "${GREEN}$description already exists at $output_path${NC}"
        fi
    }
    
    # Ask which models to download
    echo "Which AI models would you like to download?"
    
    if ask "Download GPT4All model (1.5GB)?" "Y"; then
        # GPT4All model
        download_if_not_exists \
            "https://huggingface.co/mradermacher/gpt4all-groovy.ggmlv2.q4_0/resolve/main/gpt4all-j-v1.3-groovy.bin" \
            "models/gpt4all-j-v1.3-groovy.bin" \
            "GPT4All model"
    fi
    
    if ask "Download Whisper model (500MB)?" "Y"; then
        # Whisper model
        download_if_not_exists \
            "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt" \
            "models/whisper-small.pt" \
            "Whisper model"
    fi
    
    if ask "Download Llama model (3.9GB)?" "N"; then
        # This URL is a placeholder - actual Llama models require authentication
        echo "${YELLOW}Llama models require Meta AI approval and authentication.${NC}"
        echo "Please visit https://llama.meta.com/ to request access and download manually."
        echo "Once downloaded, place the model in the models directory as 'llama-7b.ggmlv3.q4_0.bin'"
    fi
}

# Setup configuration
setup_configuration() {
    echo -e "\n${BLUE}Setting up configuration...${NC}"
    
    # Check if config.yaml exists, create if not
    if [ ! -f "config.yaml" ]; then
        echo "Creating default configuration..."
        cat > config.yaml << EOF
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
fallback_model_type: "gpt4all"

# API Keys
# Note: These should be overridden in .env file
openai_api_key: ""
huggingface_api_key: ""
google_search_api_key: ""
google_search_engine_id: ""

# Logging Settings
logging_level: "INFO"

# Security Settings
enable_system_control: false
allowed_commands:
  - "ls"
  - "dir"
  - "echo"
  - "pwd"
  - "whoami"
  - "date"
  - "time"

# GUI Settings
gui_theme: "light"
gui_font_size: 12
EOF
        echo -e "${GREEN}Created default configuration file.${NC}"
    else
        echo -e "${GREEN}Configuration file already exists.${NC}"
    fi
    
    # Create .env file for API keys if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating environment variables file..."
        cat > .env << EOF
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GOOGLE_SEARCH_API_KEY=your_google_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_google_search_engine_id_here

# Other Settings
DEBUG_MODE=true
LOGGING_LEVEL=INFO
DEFAULT_MODEL_TYPE=gpt4all
ENABLE_SYSTEM_CONTROL=false
EOF
        echo -e "${GREEN}Created .env file for API keys.${NC}"
        echo -e "${YELLOW}Please edit the .env file to add your API keys.${NC}"
    else
        echo -e "${GREEN}.env file already exists.${NC}"
    fi
    
    # Create necessary directories
    echo "Creating necessary directories..."
    mkdir -p data logs models
    
    echo -e "${GREEN}Configuration setup completed.${NC}"
}

# Test the installation
test_installation() {
    echo -e "\n${BLUE}Testing installation...${NC}"
    
    # Run a simple test
    echo "Running a simple test..."
    python -c "from src.ai_core.model_integration import AIModel; model = AIModel(); print('Model initialized successfully')"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Installation test passed!${NC}"
    else
        echo -e "${RED}Installation test failed. Please check the error messages.${NC}"
    fi
}

# Run the setup steps
main() {
    # Check if running from the project root directory
    if [ ! -f "main.py" ]; then
        echo -e "${RED}This script must be run from the project root directory.${NC}"
        echo "Please navigate to the directory containing main.py and try again."
        exit 1
    fi
    
    echo -e "${BLUE}Starting Jarvis AI setup...${NC}"
    
    # Run setup steps
    install_system_dependencies
    setup_virtual_env
    install_python_dependencies
    setup_configuration
    download_models
    
    # Test installation
    if ask "Would you like to test the installation?" "Y"; then
        test_installation
    fi
    
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}Jarvis AI Assistant setup complete!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo "To start the assistant, run:"
    echo -e "${BLUE}source venv/bin/activate${NC}"
    echo -e "${BLUE}python main.py${NC}"
    echo ""
    echo "For different modes:"
    echo -e "${BLUE}python main.py --mode gui${NC}    # GUI mode (default)"
    echo -e "${BLUE}python main.py --mode cli${NC}    # Command-line mode"
    echo -e "${BLUE}python main.py --mode voice${NC}  # Voice-controlled mode"
    echo ""
    echo "Don't forget to edit the .env file to add your API keys."
    echo ""
}

# Run the main function
main