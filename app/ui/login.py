import customtkinter as ctk
from app.utils.logger import logger
import config

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Simple placeholder label
        self.title_label = ctk.CTkLabel(
            self, 
            text="Login Screen", 
            font=ctk.CTkFont(size=config.LOGIN_TITLE_FONT_SIZE, weight="bold")
        )
        self.title_label.place(relx=0.5, rely=0.5, anchor="center")
        
        logger.info("Login screen displayed.")
