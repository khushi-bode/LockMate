import customtkinter as ctk
import config
from app.utils.logger import logger
from app.ui.splash import SplashScreen
from app.ui.login import LoginScreen
from app.ui.register import RegisterScreen
from app.ui.dashboard import DashboardScreen
from app.data.connection import initialize_database

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
        
        # Initialize frame container
        self.current_frame = None
        
        # Auto-lock variables
        self.inactivity_timer = None
        self.auto_lock_ms = 5 * 60 * 1000 # Default 5 mins, updated via Dashboard
        
        self.bind_all("<Any-KeyPress>", self.reset_inactivity_timer)
        self.bind_all("<Any-Motion>", self.reset_inactivity_timer)
        self.bind_all("<Button-1>", self.reset_inactivity_timer)
        
        # Set initial window transparency for fade-in
        self.attributes("-alpha", 0.0)
        
        # Start with splash screen
        self.show_splash_screen()
        
        # Trigger fade-in
        self.after(50, self.fade_in)
        
        logger.info(f"{config.APP_TITLE} UI initialized successfully.")
        
    def fade_in(self):
        """Gradually increases window transparency for a smooth startup effect."""
        alpha = self.attributes("-alpha")
        if alpha < 1.0:
            alpha += 0.05
            self.attributes("-alpha", alpha)
            self.after(20, self.fade_in)

    def reset_inactivity_timer(self, event=None):
        """Resets the inactivity timer when user interacts with the app."""
        if self.inactivity_timer:
            self.after_cancel(self.inactivity_timer)
            
        # Only start timer if we have an active session (Dashboard)
        if hasattr(self.current_frame, 'session_data') and getattr(self.current_frame, 'session_data', None):
            # Don't auto lock if set to 0 (Never)
            if self.auto_lock_ms > 0:
                self.inactivity_timer = self.after(self.auto_lock_ms, self.auto_lock)
            
    def auto_lock(self):
        """Locks the application due to inactivity."""
        logger.info("Session auto-locked due to inactivity.")
        if hasattr(self.current_frame, 'handle_logout'):
            self.current_frame.handle_logout()
        else:
            self.show_login_screen()
            
    def update_auto_lock(self, minutes: int):
        """Updates the auto-lock duration."""
        self.auto_lock_ms = minutes * 60 * 1000
        self.reset_inactivity_timer()

    def show_splash_screen(self):
        """Displays the splash screen and sets a timer to navigate to login."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = SplashScreen(self)
        self.current_frame.pack(expand=True, fill="both")
        
        # Wait for splash duration, then navigate to login
        self.after(config.SPLASH_DURATION, self.show_login_screen)

    def show_login_screen(self):
        """Destroys current screen and displays the login screen."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = LoginScreen(self)
        self.current_frame.pack(expand=True, fill="both")

    def show_register_screen(self):
        """Destroys current screen and displays the register screen."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = RegisterScreen(self)
        self.current_frame.pack(expand=True, fill="both")

    def show_dashboard_screen(self, session_data: dict):
        """Destroys current screen and displays the dashboard for the authenticated user."""
        if self.current_frame:
            self.current_frame.destroy()
            
        self.current_frame = DashboardScreen(self, session_data=session_data)
        self.current_frame.pack(expand=True, fill="both")


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
        # Apply theme before creating any UI widgets
        ctk.set_appearance_mode(config.APPEARANCE_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        # Initialize database
        initialize_database()
        
        app = App()
        app.mainloop()
    except Exception as e:
        logger.exception(f"An unexpected error occurred during execution: {e}")
    finally:
        logger.info("LockMate application closed.")

if __name__ == "__main__":
    main()
