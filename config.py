from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "lockmate.db"
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
LOGO_PATH = IMAGES_DIR / "logo.png"

# App Settings
APP_TITLE = "LockMate"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

# UI Settings
SPLASH_DURATION = 3000
LOGO_SIZE = (120, 120)
SIDEBAR_WIDTH = 250
ENTRY_WIDTH = 300
ENTRY_HEIGHT = 40
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 40

# Fonts
TITLE_FONT_SIZE = 36
TAGLINE_FONT_SIZE = 14
LOGIN_TITLE_FONT_SIZE = 32
LABEL_FONT_SIZE = 14
ENTRY_FONT_SIZE = 14
BUTTON_FONT_SIZE = 16

# Colors
TAGLINE_COLOR = "gray"

# Theme Settings
APPEARANCE_MODE = "Dark"
COLOR_THEME = "blue"

# Logging Settings
LOG_FILE = LOGS_DIR / "lockmate.log"
LOG_LEVEL = "INFO"

# Taglines for Splash Screen
TAGLINES = [
    "Your Trusted Password Companion",
    "Protecting Your Digital Life",
    "Secure Today. Safe Tomorrow.",
    "Smart Passwords, Smarter Security.",
    "One Vault. Complete Protection.",
]
