import customtkinter as ctk
from app.utils.logger import logger
from app.core.backup_service import BackupService
from app.data.user_repository import UserRepository
from app.ui.components.dialogs import MessageDialog


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, session_data: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.session_data = session_data
        self.user_repo = UserRepository()
        self.backup_service = BackupService()

        # Get current settings
        self.settings = self.user_repo.get_user_settings(self.session_data["user_id"])

        self.create_widgets()

    def create_widgets(self):
        card = ctk.CTkFrame(self)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card, text="Settings", font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", padx=40, pady=(30, 20))

        # Security Section
        sec_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        sec_frame.pack(fill="x", padx=40, pady=(0, 20))

        ctk.CTkLabel(sec_frame, text="Security", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )

        row1 = ctk.CTkFrame(sec_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(row1, text="Auto-Lock Timeout (minutes, 0=Never):").pack(
            side="left"
        )

        self.auto_lock_var = ctk.StringVar(
            value=str(self.settings.get("auto_lock_minutes", 5))
        )
        dropdown = ctk.CTkOptionMenu(
            row1,
            values=["1", "5", "15", "30", "0"],
            variable=self.auto_lock_var,
            command=self.save_settings,
        )
        dropdown.pack(side="right")

        row1_b = ctk.CTkFrame(sec_frame, fg_color="transparent")
        row1_b.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(row1_b, text="Password Expiry Reminder:").pack(side="left")

        exp_val = self.settings.get("expiry_days", 0)
        exp_str = f"{exp_val} Days" if exp_val > 0 else "Never"
        self.expiry_var = ctk.StringVar(value=exp_str)

        expiry_dropdown = ctk.CTkOptionMenu(
            row1_b,
            values=["30 Days", "60 Days", "90 Days", "Never"],
            variable=self.expiry_var,
            command=self.save_settings,
        )
        expiry_dropdown.pack(side="right")

        # Appearance Section
        app_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        app_frame.pack(fill="x", padx=40, pady=(0, 20))

        ctk.CTkLabel(
            app_frame, text="Appearance", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        row2 = ctk.CTkFrame(app_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(row2, text="Theme Mode:").pack(side="left")

        self.theme_var = ctk.StringVar(value=self.settings.get("theme_mode", "System"))
        theme_dropdown = ctk.CTkOptionMenu(
            row2,
            values=["System", "Dark", "Light"],
            variable=self.theme_var,
            command=self.save_settings,
        )
        theme_dropdown.pack(side="right")

        # Backup Section
        bk_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        bk_frame.pack(fill="x", padx=40, pady=(0, 40))

        ctk.CTkLabel(
            bk_frame, text="Backup & Restore", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            bk_frame,
            text="Backup your complete database or restore it.",
            text_color="gray",
        ).pack(anchor="w", padx=15, pady=(0, 15))

        btn_row = ctk.CTkFrame(bk_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(btn_row, text="Backup Vault", command=self.export_vault).pack(
            side="left", expand=True, padx=(0, 10)
        )
        ctk.CTkButton(btn_row, text="Restore Vault", command=self.import_vault).pack(
            side="right", expand=True, padx=(10, 0)
        )

        # Plaintext Export Section
        exp_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        exp_frame.pack(fill="x", padx=40, pady=(0, 40))

        ctk.CTkLabel(
            exp_frame, text="Export Data (Plaintext)", font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        ctk.CTkLabel(
            exp_frame,
            text="Export your decrypted vault to CSV or JSON formats.",
            text_color="gray",
        ).pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkButton(
            exp_frame, text="Export Vault", command=self.export_plaintext
        ).pack(padx=15, pady=(0, 15), anchor="w")

        # About Section
        about_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        about_frame.pack(fill="x", padx=40, pady=(0, 40))

        ctk.CTkLabel(about_frame, text="About", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w", padx=15, pady=(15, 5)
        )
        ctk.CTkLabel(
            about_frame,
            text="System information and version details.",
            text_color="gray",
        ).pack(anchor="w", padx=15, pady=(0, 15))

        ctk.CTkButton(about_frame, text="About LockMate", command=self.open_about).pack(
            padx=15, pady=(0, 15), anchor="w"
        )

    def open_about(self):
        from app.ui.components.about_dialog import AboutDialog

        AboutDialog(self.winfo_toplevel())

    def save_settings(self, choice):
        mins = int(self.auto_lock_var.get())
        theme = self.theme_var.get()

        exp_str = self.expiry_var.get()
        exp_days = 0 if exp_str == "Never" else int(exp_str.split()[0])

        success = self.user_repo.update_user_settings(
            self.session_data["user_id"], mins, theme, exp_days
        )
        if success:
            logger.info(
                f"Settings saved: auto_lock={mins}, theme={theme}, expiry_days={exp_days}"
            )
            ctk.set_appearance_mode(theme)
            if hasattr(self.winfo_toplevel(), "update_auto_lock"):
                self.winfo_toplevel().update_auto_lock(mins)

    def export_vault(self):
        filepath = ctk.filedialog.asksaveasfilename(
            defaultextension=".db", filetypes=[("LockMate Database", "*.db")]
        )
        if not filepath:
            return

        if self.backup_service.export_database(filepath):
            MessageDialog(
                self.winfo_toplevel(),
                title="Success",
                message="Backup created successfully!",
            )
        else:
            MessageDialog(
                self.winfo_toplevel(),
                title="Error",
                message="Failed to create backup.",
                is_error=True,
            )

    def import_vault(self):
        filepath = ctk.filedialog.askopenfilename(
            filetypes=[("LockMate Database", "*.db")]
        )
        if not filepath:
            logger.info("Restore cancelled")
            return

        def on_confirm():
            if self.backup_service.import_database(filepath):
                MessageDialog(
                    self.winfo_toplevel(),
                    title="Success",
                    message="Vault restored successfully! The application will now reload.",
                )
                # Reload application by locking the vault / returning to login screen
                if hasattr(self.master, "handle_logout"):
                    self.master.handle_logout()
                else:
                    self.winfo_toplevel().show_login_screen()
            else:
                MessageDialog(
                    self.winfo_toplevel(),
                    title="Error",
                    message="Failed to restore vault. Invalid database file.",
                    is_error=True,
                )

        def on_cancel():
            logger.info("Restore cancelled")

        from app.ui.components.dialogs import ConfirmDialog

        ConfirmDialog(
            self.winfo_toplevel(),
            title="Restore Vault",
            message="This will completely replace your current vault data and log you out. Are you sure?",
            on_confirm=on_confirm,
            on_cancel=on_cancel,
        )

    def export_plaintext(self):
        from app.core.vault_service import VaultService
        import csv
        import json

        vs = VaultService()
        items = vs.get_all_items(self.session_data)

        if not items:
            MessageDialog(
                self.winfo_toplevel(),
                title="Empty Vault",
                message="Your vault is empty. Nothing to export.",
            )
            return

        filepath = ctk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("JSON File", "*.json")],
        )
        if not filepath:
            return

        try:
            if filepath.endswith(".json"):
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(items, f, indent=4)
            else:
                with open(filepath, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "Title",
                            "URL",
                            "Username",
                            "Password",
                            "Notes",
                            "Category",
                            "Favorite",
                            "Created Date",
                            "Updated Date",
                        ]
                    )
                    for item in items:
                        writer.writerow(
                            [
                                item.get("title", ""),
                                item.get("url", ""),
                                item.get("username", ""),
                                item.get("password", ""),
                                item.get("notes", ""),
                                item.get("category", "Other"),
                                item.get("is_favorite", 0),
                                item.get("created_at", ""),
                                item.get("updated_at", ""),
                            ]
                        )

            logger.info("Exported vault to plaintext format.")
            MessageDialog(
                self.winfo_toplevel(),
                title="Success",
                message="Vault exported successfully!",
            )
        except Exception as e:
            logger.error(f"Failed to export vault: {e}")
            MessageDialog(
                self.winfo_toplevel(),
                title="Error",
                message=f"Failed to export vault: {e}",
                is_error=True,
            )
