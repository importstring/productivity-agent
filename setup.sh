#!/bin/bash

echo "Setting up Productivity Agent System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Ollama if not already installed
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Pull required Ollama models
echo "Downloading Ollama models (this may take a while)..."
ollama pull llama2:7b
ollama pull llama2:250m

# Create necessary directories
echo "Creating project directories..."
mkdir -p src/logs
mkdir -p src/data

echo "Setup complete! You can now run the system with:"
echo "python main.py" 