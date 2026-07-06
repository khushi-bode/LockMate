import sys
import sqlite3
import customtkinter as ctk
from PIL import Image
import config


class AboutDialog(ctk.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("About LockMate")
        self.geometry("450x550")
        self.resizable(False, False)

        # Center the dialog relative to master
        self.update_idletasks()
        if master:
            x = master.winfo_rootx() + (master.winfo_width() - 450) // 2
            y = master.winfo_rooty() + (master.winfo_height() - 550) // 2
            self.geometry(f"+{x}+{y}")

        self.transient(master)
        self.grab_set()

        self.create_widgets()

    def create_widgets(self):
        # Logo
        try:
            logo_img = ctk.CTkImage(
                light_image=Image.open(config.LOGO_PATH),
                dark_image=Image.open(config.LOGO_PATH),
                size=(100, 100),
            )
            ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(20, 10))
        except Exception as e:
            import logging

            logging.error(f"Failed to load logo in About dialog: {e}")

        # Title and Version
        ctk.CTkLabel(
            self, text="LockMate", font=ctk.CTkFont(size=24, weight="bold")
        ).pack()
        ctk.CTkLabel(
            self, text="Version: v1.0.0", font=ctk.CTkFont(size=14), text_color="gray"
        ).pack(pady=(0, 20))

        # Information Grid
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=40, pady=10)

        details = [
            ("Developer:", "LockMate Team"),
            ("Python Version:", sys.version.split()[0]),
            ("SQLite Version:", sqlite3.sqlite_version),
            ("CustomTkinter Version:", ctk.__version__),
            ("Encryption:", "AES-128 GCM (Fernet)"),
            ("Database Engine:", "SQLite3"),
            ("License:", "MIT License"),
            ("Build Date:", "2026-07-06"),
            ("Repository:", "github.com/lockmate"),
        ]

        for idx, (lbl, val) in enumerate(details):
            ctk.CTkLabel(info_frame, text=lbl, font=ctk.CTkFont(weight="bold")).grid(
                row=idx, column=0, sticky="w", pady=5
            )
            ctk.CTkLabel(info_frame, text=val).grid(
                row=idx, column=1, sticky="w", padx=(20, 0), pady=5
            )

        # Close Button
        ctk.CTkButton(self, text="Close", command=self.destroy, width=120).pack(
            pady=(30, 20)
        )
