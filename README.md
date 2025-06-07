# RBXAFK - Roblox AFK Tool

A Python script for maintaining activity in Roblox to prevent being kicked for inactivity.

## Requirements

- Python 3.6 or higher
- AutoHotkey installed on your system (https://www.autohotkey.com)

## Installation

### Method 1: Using pip (recommended)

```
pip install -e .
```

This will install the script and all its dependencies. Run the command from the directory containing setup.py.

### Method 2: Manual installation

Install the required dependencies:

```
pip install Pillow PyQt5 keyboard ahk pyrobloxbot configparser
```

## Usage

1. Run the script:
   ```
   python afk.py
   ```
   
2. Select your Roblox window mode (3440x1440 or 1080p Windowed)

3. Press F4 to toggle AFK mode on/off

4. Press ESC+F12 to completely exit the script

## Configuration

The script creates a config.ini file on first run with default settings. You can modify this file to adjust:

- Pixel coordinates for checks
- Expected colors
- Jump intervals
- Toggle key
