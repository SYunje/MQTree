#!/bin/bash

# Upgrade pip to its latest version
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# Install necessary Python packages from requirements.txt
echo "Installing required Python packages from requirements.txt..."
pip3 install -r requirements.txt

# Check if Arduino CLI is already installed
if ! command -v arduino-cli &> /dev/null
then
    echo "Arduino CLI not found. Installing..."
    # Install Arduino CLI
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
else
    echo "Arduino CLI is already installed."
fi

echo "Setup completed successfully."