import customtkinter as ctk
from app.utils.logger import logger
from app.core.backup_service import BackupService
from app.data.user_repository import UserRepository
from app.ui.components.dialogs import MessageDialog
import config

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, session_data: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.session_data = session_data
        self.user_repo = UserRepository()
        self.backup_service = BackupService()
        
        # Get current settings
        self.settings = self.user_repo.get_user_settings(self.session_data['user_id'])
        
        self.create_widgets()
        
    def create_widgets(self):
        card = ctk.CTkFrame(self)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(card, text="Settings", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w", padx=40, pady=(30, 20))
        
        # Security Section
        sec_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        sec_frame.pack(fill="x", padx=40, pady=(0, 20))
        
        ctk.CTkLabel(sec_frame, text="Security", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        row1 = ctk.CTkFrame(sec_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(row1, text="Auto-Lock Timeout (minutes, 0=Never):").pack(side="left")
        
        self.auto_lock_var = ctk.StringVar(value=str(self.settings.get('auto_lock_minutes', 5)))
        dropdown = ctk.CTkOptionMenu(
            row1, 
            values=["1", "5", "15", "30", "0"], 
            variable=self.auto_lock_var,
            command=self.save_settings
        )
        dropdown.pack(side="right")
        
        # Backup Section
        bk_frame = ctk.CTkFrame(card, fg_color=("gray85", "gray20"))
        bk_frame.pack(fill="x", padx=40, pady=(0, 40))
        
        ctk.CTkLabel(bk_frame, text="Backup & Restore", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(bk_frame, text="Export your vault to an encrypted file, or import from one.", text_color="gray").pack(anchor="w", padx=15, pady=(0, 15))
        
        btn_row = ctk.CTkFrame(bk_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(btn_row, text="Export Vault", command=self.export_vault).pack(side="left", expand=True, padx=(0, 10))
        ctk.CTkButton(btn_row, text="Import Vault", command=self.import_vault).pack(side="right", expand=True, padx=(10, 0))

    def save_settings(self, choice):
        mins = int(choice)
        success = self.user_repo.update_user_settings(self.session_data['user_id'], mins)
        if success:
            logger.info(f"Auto-lock set to {mins} minutes.")
            if hasattr(self.winfo_toplevel(), 'update_auto_lock'):
                self.winfo_toplevel().update_auto_lock(mins)

    def export_vault(self):
        filepath = ctk.filedialog.asksaveasfilename(defaultextension=".lockmate", filetypes=[("LockMate Backup", "*.lockmate")])
        if not filepath:
            return
            
        dialog = ctk.CTkInputDialog(text="Enter a strong password to encrypt the backup:", title="Backup Password")
        pw = dialog.get_input()
        if not pw:
            return
            
        if self.backup_service.export_vault(self.session_data, pw, filepath):
            MessageDialog(self.winfo_toplevel(), title="Success", message="Vault exported successfully!")
        else:
            MessageDialog(self.winfo_toplevel(), title="Error", message="Failed to export vault.", is_error=True)

    def import_vault(self):
        filepath = ctk.filedialog.askopenfilename(filetypes=[("LockMate Backup", "*.lockmate")])
        if not filepath:
            return
            
        dialog = ctk.CTkInputDialog(text="Enter the backup password:", title="Import Vault")
        pw = dialog.get_input()
        if not pw:
            return
            
        if self.backup_service.import_vault(self.session_data, pw, filepath):
            MessageDialog(self.winfo_toplevel(), title="Success", message="Vault imported successfully!")
        else:
            MessageDialog(self.winfo_toplevel(), title="Error", message="Failed to import vault. Incorrect password or corrupt file.", is_error=True)
