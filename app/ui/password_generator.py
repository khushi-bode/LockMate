import customtkinter as ctk
from app.utils.logger import logger
from app.core.password_generator import PasswordGeneratorService
from app.core.vault_service import VaultService
from app.ui.components.item_modal import ItemModal
import config

class PasswordGeneratorScreen(ctk.CTkFrame):
    """
    Full-featured password generator panel.
    Displayed inside the Dashboard's main content area.
    """
    def __init__(self, master, session_data: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.session_data = session_data
        self.generator = PasswordGeneratorService()
        self.vault_service = VaultService()
        self.generated_password = ""
        
        self.create_widgets()
        self.generate()  # Generate an initial password on load
        
        logger.info("Password Generator screen displayed.")

    def create_widgets(self):
        # Center the card
        self.card = ctk.CTkFrame(self)
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            self.card, 
            text="Password Generator", 
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, padx=40, pady=(30, 20), sticky="w")

        # --- Generated Password Display ---
        pw_frame = ctk.CTkFrame(self.card, fg_color=("gray85", "gray20"), corner_radius=8)
        pw_frame.grid(row=1, column=0, padx=40, pady=(0, 20), sticky="ew")
        pw_frame.grid_columnconfigure(0, weight=1)
        
        self.password_label = ctk.CTkLabel(
            pw_frame, 
            text="", 
            font=ctk.CTkFont(size=20, family="Courier"),
            wraplength=380
        )
        self.password_label.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        # Copy button inline
        self.copy_btn = ctk.CTkButton(
            pw_frame, 
            text="Copy", 
            width=70,
            command=self.copy_to_clipboard
        )
        self.copy_btn.grid(row=0, column=1, padx=(0, 10))

        # --- Strength Meter ---
        strength_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        strength_frame.grid(row=2, column=0, padx=40, pady=(0, 20), sticky="ew")
        strength_frame.grid_columnconfigure(0, weight=1)
        
        self.strength_bar = ctk.CTkProgressBar(strength_frame, height=12, corner_radius=6)
        self.strength_bar.set(0)
        self.strength_bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.strength_label = ctk.CTkLabel(strength_frame, text="", width=70, anchor="e")
        self.strength_label.grid(row=0, column=1)

        # --- Length Slider ---
        slider_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        slider_frame.grid(row=3, column=0, padx=40, pady=(0, 10), sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(slider_frame, text="Password Length", anchor="w").grid(row=0, column=0, sticky="w")
        
        self.length_value_label = ctk.CTkLabel(slider_frame, text="16", width=30, anchor="e")
        self.length_value_label.grid(row=0, column=1)
        
        self.length_slider = ctk.CTkSlider(
            self.card, 
            from_=8, to=64, 
            number_of_steps=56,
            command=self.on_slider_change
        )
        self.length_slider.set(16)
        self.length_slider.grid(row=4, column=0, padx=40, pady=(0, 20), sticky="ew")

        # --- Character Options ---
        options_frame = ctk.CTkFrame(self.card, fg_color=("gray85", "gray20"), corner_radius=8)
        options_frame.grid(row=5, column=0, padx=40, pady=(0, 20), sticky="ew")
        
        ctk.CTkLabel(
            options_frame, 
            text="Character Options", 
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        self.use_upper = ctk.BooleanVar(value=True)
        self.use_digits = ctk.BooleanVar(value=True)
        self.use_symbols = ctk.BooleanVar(value=True)
        
        checks = [
            ("Uppercase (A-Z)", self.use_upper),
            ("Digits (0-9)", self.use_digits),
            ("Symbols (!@#...)", self.use_symbols),
        ]
        
        for text, var in checks:
            ctk.CTkCheckBox(
                options_frame, 
                text=text, 
                variable=var, 
                command=self.generate
            ).pack(anchor="w", padx=15, pady=5)
            
        # Bottom spacer
        ctk.CTkFrame(options_frame, fg_color="transparent", height=10).pack()

        # --- Action Buttons ---
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.grid(row=6, column=0, padx=40, pady=(0, 30), sticky="ew")
        
        ctk.CTkButton(
            btn_frame, 
            text="Regenerate", 
            fg_color="transparent", 
            border_width=2,
            command=self.generate
        ).pack(side="left", expand=True, padx=(0, 10), fill="x")
        
        ctk.CTkButton(
            btn_frame, 
            text="Save to Vault", 
            command=self.save_to_vault
        ).pack(side="left", expand=True, padx=(10, 0), fill="x")

    def on_slider_change(self, value):
        length = int(value)
        self.length_value_label.configure(text=str(length))
        self.generate()

    def generate(self):
        length = int(self.length_slider.get())
        password = self.generator.generate(
            length=length,
            use_upper=self.use_upper.get(),
            use_digits=self.use_digits.get(),
            use_symbols=self.use_symbols.get()
        )
        self.generated_password = password
        self.password_label.configure(text=password)
        self.update_strength(password)

    def update_strength(self, password: str):
        label, color, score = self.generator.calculate_strength(password)
        self.strength_bar.set(score)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=label, text_color=color)

    def copy_to_clipboard(self):
        if self.generated_password:
            self.clipboard_clear()
            self.clipboard_append(self.generated_password)
            self.copy_btn.configure(text="Copied!")
            self.after(2000, lambda: self.copy_btn.configure(text="Copy"))
            logger.info("Password copied to clipboard.")

    def save_to_vault(self):
        if not self.generated_password:
            return
        # Open ItemModal pre-filled with the generated password
        ItemModal(
            self, 
            title_text="Save to Vault", 
            item_data={'password': self.generated_password}, 
            on_save=self.on_vault_save
        )
    
    def on_vault_save(self, data):
        self.vault_service.add_item(
            self.session_data,
            data['title'],
            data['url'],
            data['username'],
            data['password'],
            data['notes']
        )
        logger.info(f"Generated password saved to vault as '{data['title']}'.")
