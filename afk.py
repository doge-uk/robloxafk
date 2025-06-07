import time
import keyboard
import threading
import sys
import os
import webbrowser
import json
import configparser
import subprocess
from PIL import ImageGrab
from PyQt5 import QtWidgets, QtCore, QtGui
import pyrobloxbot

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")

# Import AHK Python library
ahk = None

def load_config():
    """Load configuration from file"""
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        print("Configuration loaded")
        return config
    
    # Create default config if it doesn't exist
    config["AHK"] = {"path": ""}
    
    # 3440x1440 settings (original)
    config["3440x1440"] = {
        "pixel_check_x": "1670",
        "pixel_check_y": "650",
        "expected_color_r": "58",
        "expected_color_g": "59",
        "expected_color_b": "61",
        "button_pixel_x": "1822",
        "button_pixel_y": "785",
        "expected_button_color_r": "255",
        "expected_button_color_g": "255",
        "expected_button_color_b": "255",
        "jump_interval": "5",
        "toggle_key": "f4"
    }
    
    # Add 1080p windowed settings
    config["1080p_Windowed"] = {
        "pixel_check_x": "957",
        "pixel_check_y": "477",
        "expected_color_r": "58",
        "expected_color_g": "59",
        "expected_color_b": "61",
        "button_pixel_x": "1054",
        "button_pixel_y": "606",
        "expected_button_color_r": "255",
        "expected_button_color_g": "255",
        "expected_button_color_b": "255"
    }
    
    # Add active_profile setting
    config["General"] = {"active_profile": "3440x1440"}
    
    save_config(config)
    return config

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)
    print("Configuration saved")

def initialize_ahk():
    """Initialize AHK using the specified path or try to find it automatically"""
    global ahk
    
    config = load_config()
    ahk_path = config.get("AHK", "path", fallback="")
    
    # Try to use the configured path
    if ahk_path and os.path.isfile(ahk_path):
        try:
            from ahk import AHK
            ahk = AHK(executable_path=ahk_path, timeout=10)  # Increased timeout
            print(f"AHK initialized with custom path: {ahk_path}")
            return True
        except Exception as e:
            print(f"Failed to initialize AHK with path {ahk_path}: {e}")
    
    # Try to use the AHK library with default path
    try:
        from ahk import AHK
        ahk = AHK(timeout=10)  # Increased timeout
        
        # Update config with the actual path used
        if hasattr(ahk, "executable_path") and ahk.executable_path:
            config["AHK"]["path"] = ahk.executable_path
            save_config(config)
            
        print("AHK initialized with default path")
        return True
    except ImportError:
        # Try to install the AHK library
        print("AHK Python module not found, trying to install...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ahk"])
            from ahk import AHK
            ahk = AHK()
            print("AHK Python module installed successfully")
            return True
        except:
            print("Failed to install AHK Python module")
            return False
    except Exception as e:
        print(f"Failed to initialize AHK: {e}")
        return False

def select_ahk_executable():
    """Opens a file dialog to select the AutoHotkey executable"""
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    
    file_dialog = QtWidgets.QFileDialog()
    file_dialog.setWindowTitle("Select AutoHotkey Executable")
    file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    file_dialog.setNameFilter("Executable Files (*.exe)")
    
    # Default to Program Files if it exists
    default_dir = r"C:\Program Files\AutoHotkey"
    if os.path.isdir(default_dir):
        file_dialog.setDirectory(default_dir)
    
    if file_dialog.exec_():
        selected_files = file_dialog.selectedFiles()
        if selected_files:
            ahk_path = selected_files[0]
            
            # Update config
            config = load_config()
            config["AHK"]["path"] = ahk_path
            save_config(config)
            
            print(f"Selected AHK executable: {ahk_path}")
            return ahk_path
    
    return None

def check_ahk_installation():
    """Check if AutoHotkey is installed and configured"""
    global ahk
    
    # First check if we have a valid path in config
    config = load_config()
    ahk_path = config.get("AHK", "path", fallback="")
    
    # If we have a configured path, use it without additional checking
    if ahk_path and os.path.isfile(ahk_path):
        print(f"Using AutoHotkey from configured path: {ahk_path}")
        
        # Try to initialize AHK with this path directly
        try:
            from ahk import AHK
            ahk = AHK(executable_path=ahk_path)
            print("AHK initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing AHK with configured path: {e}")
    
    # If no path configured or failed to initialize, try with default path
    try:
        from ahk import AHK
        ahk = AHK()
        
        # If successful, update the config with the path
        if hasattr(ahk, "executable_path") and ahk.executable_path:
            config["AHK"]["path"] = ahk.executable_path
            save_config(config)
            print(f"AHK initialized with default path: {ahk.executable_path}")
        else:
            print("AHK initialized with unknown path")
            
        return True
    except Exception as e:
        print(f"Failed to initialize AHK with default path: {e}")
    
    # If all automatic methods failed, ask user to select the executable
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("AutoHotkey Required")
    msg_box.setText("AutoHotkey is required but couldn't be found automatically.")
    msg_box.setInformativeText("Please select the AutoHotkey executable (usually found in C:\\Program Files\\AutoHotkey\\AutoHotkey.exe)")
    select_btn = msg_box.addButton("Select AutoHotkey", QtWidgets.QMessageBox.YesRole)
    cancel_btn = msg_box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
    
    msg_box.exec_()
    
    if msg_box.clickedButton() == select_btn:
        ahk_path = select_ahk_executable()
        if ahk_path:
            try:
                from ahk import AHK
                ahk = AHK(executable_path=ahk_path)
                print(f"AHK initialized with selected path: {ahk_path}")
                return True
            except Exception as e:
                print(f"Failed to initialize AHK with selected path: {e}")
    
    return False

# Constants
SCRIPT_VERSION = "1.0.2"  # Add version tracking
PIXEL_TO_CHECK = (1670, 650)
EXPECTED_COLOR = (58, 59, 61)
BUTTON_PIXEL = (1822, 785)
EXPECTED_BUTTON_COLOR = (255, 255, 255)
JUMP_INTERVAL = 5  # seconds
TOGGLE_KEY = "f4"  # Using simpler keyboard library

# Global state
running = False
app = None
overlay = None

def check_pixel_color(x, y, expected_color, tolerance=10):
    """Check if pixel at (x,y) matches the expected RGB color within a tolerance"""
    try:
        screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        actual_color = screenshot.getpixel((0, 0))
        
        # Check if each RGB component is within the tolerance range
        r_match = abs(actual_color[0] - expected_color[0]) <= tolerance
        g_match = abs(actual_color[1] - expected_color[1]) <= tolerance
        b_match = abs(actual_color[2] - expected_color[2]) <= tolerance
        
        return r_match and g_match and b_match
    except Exception as e:
        print(f"Error checking pixel color: {e}")
        return False

def show_pixel_info():
    """Debug function to show the actual color of pixels we're checking"""
    try:
        pixel1 = ImageGrab.grab(bbox=(PIXEL_TO_CHECK[0], PIXEL_TO_CHECK[1], 
                                    PIXEL_TO_CHECK[0]+1, PIXEL_TO_CHECK[1]+1)).getpixel((0, 0))
        pixel2 = ImageGrab.grab(bbox=(BUTTON_PIXEL[0], BUTTON_PIXEL[1], 
                                    BUTTON_PIXEL[0]+1, BUTTON_PIXEL[1]+1)).getpixel((0, 0))
        
        # Show actual colors and whether they match within tolerance
        p1_match = "Match" if check_pixel_color(*PIXEL_TO_CHECK, EXPECTED_COLOR) else "No Match"
        p2_match = "Match" if check_pixel_color(*BUTTON_PIXEL, EXPECTED_BUTTON_COLOR) else "No Match"
        
        print(f"Debug - Pixel 1 color: {pixel1}, Expected: {EXPECTED_COLOR} - {p1_match}")
        print(f"Debug - Pixel 2 color: {pixel2}, Expected: {EXPECTED_BUTTON_COLOR} - {p2_match}")
    except Exception as e:
        print(f"Error in show_pixel_info: {e}")

def load_pixel_coordinates():
    """Load pixel coordinates from the active profile in config"""
    global PIXEL_TO_CHECK, EXPECTED_COLOR, BUTTON_PIXEL, EXPECTED_BUTTON_COLOR, JUMP_INTERVAL, TOGGLE_KEY
    
    config = load_config()
    
    # Get the active profile
    active_profile = config.get("General", "active_profile", fallback="3440x1440")
    
    # Ensure the profile exists, fall back to 3440x1440 if not
    if not config.has_section(active_profile):
        print(f"Warning: Profile {active_profile} not found, using default 3440x1440")
        active_profile = "3440x1440"
        
        # If even 3440x1440 doesn't exist, create it with default values
        if not config.has_section("3440x1440"):
            print("Creating default 3440x1440 profile")
            config["3440x1440"] = {
                "pixel_check_x": "1670",
                "pixel_check_y": "650",
                "expected_color_r": "58",
                "expected_color_g": "59",
                "expected_color_b": "61",
                "button_pixel_x": "1822",
                "button_pixel_y": "785", 
                "expected_button_color_r": "255",
                "expected_button_color_g": "255",
                "expected_button_color_b": "255",
                "jump_interval": "5",
                "toggle_key": "f4"
            }
            save_config(config)
    
    # Load settings from the active profile
    profile = config[active_profile]
    
    PIXEL_TO_CHECK = (
        int(profile.get("pixel_check_x", "1670")),
        int(profile.get("pixel_check_y", "650"))
    )
    
    EXPECTED_COLOR = (
        int(profile.get("expected_color_r", "58")),
        int(profile.get("expected_color_g", "59")),
        int(profile.get("expected_color_b", "61"))
    )
    
    BUTTON_PIXEL = (
        int(profile.get("button_pixel_x", "1822")),
        int(profile.get("button_pixel_y", "785"))
    )
    
    EXPECTED_BUTTON_COLOR = (
        int(profile.get("expected_button_color_r", "255")),
        int(profile.get("expected_button_color_g", "255")),
        int(profile.get("expected_button_color_b", "255"))
    )
    
    # These values should be in each profile
    JUMP_INTERVAL = int(profile.get("jump_interval", "5"))
    TOGGLE_KEY = profile.get("toggle_key", "f4")
    
    print(f"Loaded profile: {active_profile}")
    print(f"Check pixel: {PIXEL_TO_CHECK}, Button pixel: {BUTTON_PIXEL}")

def switch_profile(profile_name):
    """Switch to a different resolution profile"""
    config = load_config()
    
    if not config.has_section(profile_name):
        print(f"Profile {profile_name} does not exist!")
        return False
    
    # Make sure the General section exists
    if not config.has_section("General"):
        config.add_section("General")
    
    # Update the active profile
    config["General"]["active_profile"] = profile_name
    save_config(config)
    
    # Reload the coordinates
    load_pixel_coordinates()
    
    print(f"Switched to profile: {profile_name}")
    return True

def create_resolution_menu():
    """Create a menu for selecting different resolution profiles"""
    menu = QtWidgets.QMenu()
    
    config = load_config()
    active_profile = config.get("General", "active_profile", fallback="Settings")
    
    # Add profiles from config
    for section in config.sections():
        if section not in ["AHK", "General"]:
            action = menu.addAction(section)
            action.setCheckable(True)
            action.setChecked(section == active_profile)
            action.triggered.connect(lambda checked, s=section: switch_profile(s))
    
    return menu

class OverlayWidget(QtWidgets.QWidget):
    """Custom overlay widget that stays on top"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        
        # Set up the layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Create label with bigger, red text
        self.label = QtWidgets.QLabel(f"AFK MODE ACTIVE - PRESS {TOGGLE_KEY.upper()} TO STOP")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: #FF0000; font-size: 24px; font-weight: bold; padding: 20px;")
        
        # Add label to layout (removed resolution selection button)
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Set size for overlay (made a bit smaller since we removed the button)
        self.resize(600, 80)
        
        # Center on screen
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
    def show_overlay(self):
        """Show the overlay"""
        self.show()
    
    def hide_overlay(self):
        """Hide the overlay"""
        self.hide()

def create_overlay():
    """Create a simple overlay window showing the script is active"""
    global overlay
    
    if overlay is None:
        overlay = OverlayWidget()
    
    overlay.show_overlay()
    return overlay

def run_ahk_script():
    """Use AHK Python library or click.exe to perform clicking"""
    global ahk
    
    try:
        if ahk is not None:
            # Instead of using win_activate which may cause the error,
            # use a direct AHK script execution
            script = f"""
            WinActivate, Roblox
            Sleep 200
            Click {BUTTON_PIXEL[0]}, {BUTTON_PIXEL[1]}
            """
            
            # Run the script directly
            result = ahk.run_script(script)
            print(f"Clicked at {BUTTON_PIXEL} using AHK script")
            return True
            
        return False  # AHK not available
    except Exception as e:
        print(f"Failed to execute AHK command: {e}")
        return False

def afk_loop():
    """The main AFK functionality loop"""
    global running
    
    last_jump_time = 0
    while running:
        try:
            # Debug pixel info occasionally
            if time.time() % 10 < 0.1:  # Print every ~10 seconds
                show_pixel_info()
            
            # Check if it's time to jump
            current_time = time.time()
            if current_time - last_jump_time >= JUMP_INTERVAL:
                pyrobloxbot.jump()  # Use the jump function from pyrobloxbot
                last_jump_time = current_time
                print("Jumped")
            
            # Check pixel conditions and click if needed
            if (check_pixel_color(*PIXEL_TO_CHECK, EXPECTED_COLOR) and 
                check_pixel_color(*BUTTON_PIXEL, EXPECTED_BUTTON_COLOR)):
                run_ahk_script()
                time.sleep(0.5)  # Short delay after clicking
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
            
        except Exception as e:
            print(f"Error in AFK loop: {e}")
            time.sleep(1)  # Delay on error

def toggle_afk():
    """Toggle the AFK mode on/off"""
    global running, overlay
    
    running = not running
    
    if running:
        print("AFK mode activated")
        if app is not None:
            overlay = create_overlay()
            
            # Start AFK loop in a separate thread
            afk_thread = threading.Thread(target=afk_loop)
            afk_thread.daemon = True
            afk_thread.start()
    else:
        print("AFK mode deactivated")
        if overlay:
            overlay.hide_overlay()

def show_simple_config_dialog():
    """Show a simple configuration dialog with just two options"""
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle("Select Roblox Window Mode")
    msg_box.setText("Which Roblox window mode are you using?")
    
    # Add buttons for the two main profiles
    fullscreen_btn = msg_box.addButton("3440x1440", QtWidgets.QMessageBox.ActionRole)
    windowed_btn = msg_box.addButton("1080p Windowed", QtWidgets.QMessageBox.ActionRole)
    cancel_btn = msg_box.addButton(QtWidgets.QMessageBox.Cancel)
    
    # Show the dialog
    msg_box.exec_()
    
    # Handle the result
    if msg_box.clickedButton() == fullscreen_btn:
        switch_profile("3440x1440")  # Changed from "Settings"
        return True
    elif msg_box.clickedButton() == windowed_btn:
        switch_profile("1080p_Windowed")
        return True
    else:
        return False

def main():
    """Main function to run the AFK script"""
    global app, overlay
    
    print(r"""   
   _____  _______________  __.    ____________________________.________________________
  /  _  \ \_   _____/    |/ _|   /   _____/\_   ___ \______   \   \______   \__    ___/
 /  /_\  \ |    __) |      <     \_____  \ /    \  \/|       _/   ||     ___/ |    |   
/    |    \|     \  |    |  \    /        \\     \___|    |   \   ||    |     |    |   
\____|__  /\___  /  |____|__ \  /_______  / \______  /____|_  /___||____|     |____|   
        \/     \/           \/          \/         \/       \/                                 
    """)
    
    # Print version separately to allow for variable substitution
    print(f"V{SCRIPT_VERSION} - Doge's AFK Script")
    
    # Load configuration
    config = load_config()
    
    # Initialize the Qt application
    app = QtWidgets.QApplication(sys.argv)
    
    # Show simple configuration dialog
    if not show_simple_config_dialog():
        print("Configuration cancelled. Exiting.")
        return
    
    # Load pixel coordinates from active profile
    load_pixel_coordinates()
    
    # Check for AHK setup
    if not check_ahk_installation():
        error_box = QtWidgets.QMessageBox()
        error_box.setWindowTitle("AutoHotkey Required")
        error_box.setText("This script requires AutoHotkey to function.")
        error_box.setInformativeText("Please install AutoHotkey from https://www.autohotkey.com/download/ahk-install.exe and restart this script.")
        error_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        error_box.exec_()
        
        # Open the AHK download page
        webbrowser.open("https://www.autohotkey.com/download/ahk-install.exe")
        
        print("Script terminated: AutoHotkey is required but not found.")
        sys.exit(1)
    
    print(f"Press {TOGGLE_KEY.upper()} to toggle AFK mode")
    
    # Register the toggle hotkey
    keyboard.add_hotkey(TOGGLE_KEY, toggle_afk)
    
    # Add a way to completely exit the script
    keyboard.add_hotkey('esc+f12', lambda: sys.exit())
    
    # Create a dummy widget to keep the application running
    dummy = QtWidgets.QWidget()
    
    # Keep the script running using Qt event loop
    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("Script terminated by user")
    finally:
        # Clean up
        if overlay:
            overlay.hide_overlay()

if __name__ == "__main__":
    main()
