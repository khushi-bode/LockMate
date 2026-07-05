import customtkinter as ctk
import config
from app.utils.logger import logger

class App(ctk.CTk):
    """
    Main Application Window for LockMate.
    Initializes the GUI and applies basic configuration.
    """
    def __init__(self):
        super().__init__()
        
        # Configure window title
        self.title(config.APP_TITLE)
        
        # Center the window with the configured dimensions
        self.center_window(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # Apply theme settings
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        logger.info(f"{config.APP_TITLE} UI initialized successfully.")

    def center_window(self, width, height):
        """
        Centers the window on the screen based on the provided width and height.
        """
        self.geometry(f"{width}x{height}")
        self.update_idletasks()
        
        # Calculate x and y coordinates for the center of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        
        self.geometry(f"{width}x{height}+{x}+{y}")

def main():
    """
    Application entry point. Initializes the logger and starts the main event loop.
    """
    logger.info("Starting LockMate application bootstrap...")
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        logger.exception(f"An unexpected error occurred during execution: {e}")
    finally:
        logger.info("LockMate application closed.")

if __name__ == "__main__":
    main()
