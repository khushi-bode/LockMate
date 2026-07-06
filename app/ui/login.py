import customtkinter as ctk
from app.utils.logger import logger
from app.security.auth import AuthService
import config


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.auth_service = AuthService()

        # Center frame to hold contents
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Add padding to content frame
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Login to LockMate",
            font=ctk.CTkFont(size=config.LOGIN_TITLE_FONT_SIZE, weight="bold"),
        )
        self.title_label.grid(row=0, column=0, pady=(40, 10), padx=40)

        # Status Label
        self.status_label = ctk.CTkLabel(self.content_frame, text="", text_color="red")
        self.status_label.grid(row=1, column=0, pady=(0, 10))

        # Username
        self.username_entry = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="Username",
            width=config.ENTRY_WIDTH,
            height=config.ENTRY_HEIGHT,
            font=ctk.CTkFont(size=config.ENTRY_FONT_SIZE),
        )
        self.username_entry.grid(row=2, column=0, pady=(0, 20), padx=40)

        # Password Container
        self.password_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.password_frame.grid(row=3, column=0, pady=(0, 10), padx=40)

        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="Master Password",
            show="*",
            width=config.ENTRY_WIDTH - 60,
            height=config.ENTRY_HEIGHT,
            font=ctk.CTkFont(size=config.ENTRY_FONT_SIZE),
        )
        self.password_entry.pack(side="left", padx=(0, 10))

        self.show_password_btn = ctk.CTkButton(
            self.password_frame,
            text="Show",
            width=50,
            height=config.ENTRY_HEIGHT,
            command=self.toggle_password_visibility,
        )
        self.show_password_btn.pack(side="left")

        # Remember Me
        self.remember_me_checkbox = ctk.CTkCheckBox(
            self.content_frame,
            text="Remember Me",
            font=ctk.CTkFont(size=config.LABEL_FONT_SIZE),
        )
        self.remember_me_checkbox.grid(
            row=4, column=0, sticky="w", pady=(0, 20), padx=40
        )

        # Login Button
        self.login_btn = ctk.CTkButton(
            self.content_frame,
            text="Login",
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            font=ctk.CTkFont(size=config.BUTTON_FONT_SIZE, weight="bold"),
            command=self.handle_login,
        )
        self.login_btn.grid(row=5, column=0, pady=(0, 10), padx=40)

        # Register Button
        self.register_btn = ctk.CTkButton(
            self.content_frame,
            text="Create an Account",
            width=config.BUTTON_WIDTH,
            height=config.BUTTON_HEIGHT,
            fg_color="transparent",
            border_width=2,
            font=ctk.CTkFont(size=config.BUTTON_FONT_SIZE, weight="bold"),
            command=self.master.show_register_screen,
        )
        self.register_btn.grid(row=6, column=0, pady=(0, 40), padx=40)

        logger.info("Login screen displayed.")

    def toggle_password_visibility(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.show_password_btn.configure(text="Hide")
        else:
            self.password_entry.configure(show="*")
            self.show_password_btn.configure(text="Show")

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        success, message, session_data = self.auth_service.login_user(
            username, password
        )

        if success:
            self.status_label.configure(text=message, text_color="green")
            self.after(500, lambda: self.master.show_dashboard_screen(session_data))
        else:
            self.status_label.configure(text=message, text_color="red")
