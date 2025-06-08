from setuptools import setup, find_packages

setup(
    name="RBXAFK",
    version="1.0.0",
    description="Roblox AFK Script for keeping your character active",
    author="Script User",
    packages=find_packages(),
    install_requires=[
        'Pillow',  # For ImageGrab
        'PyQt5',   # For the GUI components
        'keyboard',  # For keyboard input
        'ahk',     # For AutoHotkey integration
        'pyrobloxbot',  # For Roblox bot functionality
        'configparser',  # For config file management
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'rbxafk=afk:main',
        ],
    },
)
