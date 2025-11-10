#!/bin/bash

# 3dPot Central Control System Setup Script
# Automated installation and configuration

set -e

echo "🏭 3dPot Central Control System - Setup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_status "Detected OS: $OS"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    print_status "Python version $python_version is compatible"
else
    print_error "Python 3.8+ required, found $python_version"
    exit 1
fi

# Check pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 not found. Please install pip3 first."
    exit 1
fi

# Create virtual environment
print_header "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_header "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_header "Installing Python dependencies..."
pip install -r requirements.txt

# Create directories
print_header "Creating necessary directories..."
mkdir -p logs
mkdir -p data
mkdir -p backups
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Set permissions
print_header "Setting permissions..."
chmod +x central_control.py
chmod +x setup.sh

# Create config file if it doesn't exist
if [ ! -f "config.json" ]; then
    print_header "Creating configuration file..."
    cat > config.json << 'EOF'
{
  "esp32": {
    "url": "http://192.168.1.100",
    "timeout": 5,
    "weight_low_threshold": 100.0
  },
  "rpi_qc": {
    "url": "http://192.168.1.101", 
    "timeout": 5
  },
  "arduino": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600
  },
  "database": {
    "path": "central_control.db"
  }
}
EOF
    print_status "Configuration file created"
    print_warning "Please edit config.json with your network settings"
else
    print_status "Configuration file already exists"
fi

# Setup Arduino permissions (Linux only)
if [[ "$OS" == "linux" ]]; then
    print_header "Setting up Arduino permissions..."
    if groups $USER | grep -q dialout; then
        print_status "User already in dialout group"
    else
        print_warning "Adding user to dialout group for serial access..."
        sudo usermod -a -G dialout $USER
        print_warning "Please reboot your system to apply the permission changes"
    fi
fi

# Create systemd service (Linux only)
if [[ "$OS" == "linux" ]]; then
    print_header "Creating systemd service..."
    cat > 3dpot-central.service << EOF
[Unit]
Description=3dPot Central Control System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python central_control.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    print_status "Systemd service file created"
    print_warning "To enable the service, run:"
    echo "  sudo cp 3dpot-central.service /etc/systemd/system/"
    echo "  sudo systemctl enable 3dpot-central"
    echo "  sudo systemctl start 3dpot-central"
fi

# Create startup script
print_header "Creating startup script..."
cat > start_central.sh << 'EOF'
#!/bin/bash
# 3dPot Central Control System Startup Script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🏭 Starting 3dPot Central Control System..."
echo "Dashboard will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop"

python central_control.py
EOF

chmod +x start_central.sh
print_status "Startup script created"

# Create development script
cat > dev_central.sh << 'EOF'
#!/bin/bash
# 3dPot Central Control System Development Mode

cd "$(dirname "$0")"
source venv/bin/activate

echo "🏭 Starting 3dPot Central Control System (Development Mode)..."
echo "Dashboard will be available at: http://localhost:5000"
echo "Debug mode enabled"

python central_control.py
EOF

chmod +x dev_central.sh
print_status "Development startup script created"

# Test installation
print_header "Testing installation..."
python3 -c "
import flask
import flask_socketio
import requests
import serial
import sqlite3
print('✓ All dependencies installed correctly')
"

if [ $? -eq 0 ]; then
    print_status "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Create quick start guide
print_header "Creating quick start guide..."
cat > QUICK_START.md << 'EOF'
# 3dPot Central Control System - Quick Start

## First Time Setup
1. Edit `config.json` with your network settings
2. Ensure all hardware is connected
3. Run the startup script

## Starting the System
```bash
./start_central.sh
```

## Development Mode
```bash
./dev_central.sh
```

## Accessing the Dashboard
Open your browser to: http://localhost:5000

## Testing Individual Components
```bash
# Test ESP32 connection
curl http://192.168.1.100/api/status

# Test Arduino (check /dev/ttyUSB0)
ls -la /dev/ttyUSB*

# Test RPi QC
curl http://192.168.1.101/api/status
```

## Troubleshooting
- Check logs in `central_control.log`
- Verify network connectivity
- Ensure proper permissions for serial ports
- Run in development mode for more verbose output

## System Requirements
- Python 3.8+
- Arduino connected via USB
- ESP32 powered and connected to WiFi
- Raspberry Pi with camera and network access
EOF

print_status "Quick start guide created"

# Create sample data script
print_header "Creating sample data generator..."
cat > generate_sample_data.py << 'EOF'
#!/usr/bin/env python3
"""
Generate sample data for testing the 3dPot Central Control System
"""
import json
import random
from datetime import datetime, timedelta

def generate_sample_config():
    """Generate sample configuration"""
    return {
        "esp32": {
            "url": "http://192.168.1.100",
            "weight": random.uniform(50, 500),
            "status": "ready"
        },
        "arduino": {
            "port": "/dev/ttyUSB0",
            "speed": random.randint(10, 100),
            "status": "ready"
        },
        "rpi_qc": {
            "url": "http://192.168.1.101",
            "qc_status": "waiting",
            "camera": "connected"
        }
    }

if __name__ == "__main__":
    config = generate_sample_config()
    with open('sample_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("Sample config generated: sample_config.json")
EOF

chmod +x generate_sample_data.py

# Final summary
echo ""
print_header "Installation Complete!"
echo "========================"
echo ""
print_status "3dPot Central Control System is ready to use!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your network settings"
echo "2. Connect your hardware (Arduino, ESP32, RPi)"
echo "3. Start the system: ./start_central.sh"
echo "4. Open dashboard: http://localhost:5000"
echo ""
echo "Files created:"
echo "  - venv/                (virtual environment)"
echo "  - config.json          (configuration file)"
echo "  - start_central.sh     (startup script)"
echo "  - dev_central.sh       (development script)"
echo "  - QUICK_START.md       (quick start guide)"
echo ""
if [[ "$OS" == "linux" ]]; then
    echo "Optional - Enable as system service:"
    echo "  sudo cp 3dpot-central.service /etc/systemd/system/"
    echo "  sudo systemctl enable 3dpot-central"
    echo "  sudo systemctl start 3dpot-central"
fi
echo ""
print_status "Happy monitoring! 🏭✨"
echo ""

# Prompt to start the system
read -p "Would you like to start the system now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting 3dPot Central Control System..."
    ./start_central.sh
fi