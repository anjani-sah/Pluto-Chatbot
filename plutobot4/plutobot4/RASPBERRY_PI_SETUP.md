# Pluto Bot - Raspberry Pi Setup Guide

## 🚨 Quick Fix for Virtual Environment Issues

If you're getting "Failed to activate virtual environment" errors, follow these steps:

### Step 1: Run Diagnostics
```bash
./diagnose_pi.sh
```

### Step 2: Install Missing Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python essentials
sudo apt install -y python3-venv python3-pip python3-distutils python3-dev

# Install audio dependencies  
sudo apt install -y alsa-utils portaudio19-dev libasound2-dev

# Install build tools (for compiling packages)
sudo apt install -y build-essential
```

### Step 3: Reset Virtual Environment
```bash
# Remove old venv if it exists
rm -rf venv

# Try creating new venv
python3 -m venv venv

# Test activation manually
source venv/bin/activate
```

### Step 4: Run Pluto
```bash
# Normal startup
./start_pluto.sh

# Or with diagnostics first
./start_pluto.sh --diagnose

# Or reset everything
./start_pluto.sh --reset-venv
```

## 🔧 Common Issues and Fixes

### Issue: "python3-venv not found"
```bash
sudo apt update
sudo apt install -y python3-venv
```

### Issue: "Failed to build wheel for X package"
```bash
sudo apt install -y build-essential python3-dev
```

### Issue: "No module named 'distutils'"  
```bash
sudo apt install -y python3-distutils
```

### Issue: "Virtual environment creation failed"
Try alternative method:
```bash
# Install virtualenv as alternative
pip3 install --user virtualenv
python3 -m virtualenv venv
```

### Issue: "Permission denied"
Make sure scripts are executable:
```bash
chmod +x start_pluto.sh
chmod +x diagnose_pi.sh
```

## 🍓 Raspberry Pi Specific Notes

1. **GPIO Access**: The script automatically detects if you're on a Pi and installs RPi.GPIO
2. **Audio**: ALSA tools are installed for microphone and speaker support  
3. **Performance**: Some packages may take longer to install on Pi - be patient
4. **Memory**: Make sure you have at least 1GB free space for packages

## 🆘 Still Having Issues?

1. **Check Python version**: `python3 --version` (should be 3.8+)
2. **Check available space**: `df -h` (need at least 1GB)
3. **Check permissions**: Make sure you own the Plutobot2 directory
4. **Check network**: `ping google.com` (need internet for package downloads)

## 📞 Debug Information to Share

If you're still stuck, run this and share the output:
```bash
./diagnose_pi.sh > debug_info.txt
cat debug_info.txt
```

This will help identify the exact issue with your setup.
