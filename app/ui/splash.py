import random
import customtkinter as ctk
from PIL import Image
import config
from app.utils.logger import logger

class SplashScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Center frame to hold contents
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        try:
            logo_image = ctk.CTkImage(
                light_image=Image.open(config.LOGO_PATH),
                dark_image=Image.open(config.LOGO_PATH),
                size=config.LOGO_SIZE
            )
            self.logo_label = ctk.CTkLabel(self.content_frame, image=logo_image, text="")
            self.logo_label.pack(pady=(0, 20))
        except Exception as e:
            logger.error(f"Failed to load logo on splash screen: {e}")
            
        # App Title
        self.title_label = ctk.CTkLabel(
            self.content_frame, 
            text=config.APP_TITLE, 
            font=ctk.CTkFont(size=config.TITLE_FONT_SIZE, weight="bold")
        )
        self.title_label.pack(pady=(0, 10))
        
        # Tagline
        tagline = random.choice(config.TAGLINES)
        self.tagline_label = ctk.CTkLabel(
            self.content_frame, 
            text=tagline,
            font=ctk.CTkFont(size=config.TAGLINE_FONT_SIZE),
            text_color=config.TAGLINE_COLOR
        )
        self.tagline_label.pack(pady=(0, 30))
        
        # Loading Indicator
        self.progress = ctk.CTkProgressBar(self.content_frame, width=200, mode="indeterminate")
        self.progress.pack()
        self.progress.start()
        
        logger.info(f"Splash screen initialized with tagline: '{tagline}'")
