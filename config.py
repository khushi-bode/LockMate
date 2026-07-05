import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"

# App Settings
APP_TITLE = "LockMate"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# Theme Settings
APPEARANCE_MODE = "Dark"
COLOR_THEME = "blue"

# Logging Settings
LOG_FILE = LOGS_DIR / "lockmate.log"
LOG_LEVEL = "INFO"
