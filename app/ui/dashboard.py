import customtkinter as ctk
from app.utils.logger import logger
from app.core.vault_service import VaultService
from app.ui.components.item_modal import ItemModal
from app.ui.password_generator import PasswordGeneratorScreen
from app.ui.settings import SettingsScreen
import config

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, session_data: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.session_data = session_data
        self.vault_service = VaultService()
        self.active_panel = None
        
        # Configure layout (2 columns: Sidebar, Main Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.show_vault_panel()  # Default view
        
        logger.info(f"Dashboard screen displayed for user: {self.session_data['username']}")

    # ─────────────────────────────────────────
    #  Sidebar
    # ─────────────────────────────────────────
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=config.SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Spacer pushes logout down
        
        # App logo / title
        ctk.CTkLabel(
            self.sidebar_frame, 
            text=config.APP_TITLE, 
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 30))
        
        # Navigation definitions: (label, callback)
        nav_items = [
            ("All Items",           self.show_vault_panel),
            ("Password Generator",  self.show_generator_panel),
            ("Settings",            self.show_settings_panel),
        ]
        
        self.nav_buttons = []
        for idx, (label, callback) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar_frame, 
                text=label, 
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                command=callback
            )
            btn.grid(row=idx+1, column=0, padx=20, pady=10, sticky="ew")
            self.nav_buttons.append(btn)
            
        # Logout button
        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="Logout", 
            fg_color="#d63031", 
            hover_color="#b22828",
            command=self.handle_logout
        )
        self.logout_btn.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

    # ─────────────────────────────────────────
    #  Panel Switching
    # ─────────────────────────────────────────
    def _clear_panel(self):
        if self.active_panel is not None:
            self.active_panel.destroy()
            self.active_panel = None

    def show_vault_panel(self):
        self._clear_panel()
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(3, weight=1)
        self.active_panel = panel
        self._build_vault_panel(panel)

    def show_generator_panel(self):
        self._clear_panel()
        panel = PasswordGeneratorScreen(self, session_data=self.session_data)
        panel.grid(row=0, column=1, sticky="nsew")
        self.active_panel = panel

    def show_settings_panel(self):
        self._clear_panel()
        panel = SettingsScreen(self, session_data=self.session_data)
        panel.grid(row=0, column=1, sticky="nsew")
        self.active_panel = panel

    # ─────────────────────────────────────────
    #  Vault Panel
    # ─────────────────────────────────────────
    def _build_vault_panel(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(3, weight=1)
        
        # Welcome
        ctk.CTkLabel(
            parent, 
            text=f"Welcome back, {self.session_data['username']}!", 
            font=ctk.CTkFont(size=32, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))
        
        # Stats Cards
        self.stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 20))
        
        # We will populate them in refresh_list
        self.stat_total = self.create_stat_card(self.stats_frame, "Total Items", "0")
        self.stat_weak = self.create_stat_card(self.stats_frame, "Weak Passwords", "0")
        self.stat_reused = self.create_stat_card(self.stats_frame, "Reused Passwords", "0")
        self.stat_old = self.create_stat_card(self.stats_frame, "Old Passwords (>90d)", "0")
        
        # Search + Add button row
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(
            actions_frame, 
            placeholder_text="Search vault...", 
            width=300
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.handle_search)
        
        ctk.CTkButton(
            actions_frame, 
            text="+ Add Password", 
            command=self.open_add_modal
        ).pack(side="right")
        
        # Column headers
        header = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"), corner_radius=5)
        header.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 5))
        header.grid_columnconfigure(0, weight=3)
        header.grid_columnconfigure(1, weight=2)
        header.grid_columnconfigure(2, weight=1)
        
        ctk.CTkLabel(header, text="Title",    font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(header, text="Username", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(header, text="Actions",  font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, sticky="e", padx=10, pady=5)

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.list_frame.grid(row=4, column=0, sticky="nsew", padx=40, pady=(0, 40))
        
        self.refresh_list()

    def create_stat_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="gray")
        title_label.pack(pady=(15, 5), padx=15)
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(pady=(0, 15), padx=15)
        return value_label

    # ─────────────────────────────────────────
    #  Vault CRUD
    # ─────────────────────────────────────────
    def handle_search(self, event=None):
        query = self.search_entry.get().strip()
        items = (self.vault_service.search_items(self.session_data, query) 
                 if query else 
                 self.vault_service.get_all_items(self.session_data))
        self.render_items(items)

    def refresh_list(self):
        items = self.vault_service.get_all_items(self.session_data)
        
        # Update health stats
        if hasattr(self, 'stat_total'):
            health = self.vault_service.get_vault_health(self.session_data)
            self.stat_total.configure(text=str(health['total']))
            
            # Color warnings
            self.stat_weak.configure(text=str(health['weak']), text_color="#d63031" if health['weak'] > 0 else "gray90")
            self.stat_reused.configure(text=str(health['reused']), text_color="#d63031" if health['reused'] > 0 else "gray90")
            self.stat_old.configure(text=str(health['old']), text_color="#fdcb6e" if health['old'] > 0 else "gray90")
            
        self.render_items(items)

    def render_items(self, items):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        if not items:
            ctk.CTkLabel(self.list_frame, text="No items found in vault.", text_color="gray").pack(pady=20)
            return
            
        for idx, item in enumerate(items):
            bg_color = ("gray95", "gray15") if idx % 2 == 0 else ("gray90", "gray10")
            row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=2)
            row.grid_columnconfigure(2, weight=1)
            
            ctk.CTkLabel(row, text=item['title']).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            ctk.CTkLabel(row, text=item.get('username', '')).grid(row=0, column=1, sticky="w", padx=10, pady=10)
            
            af = ctk.CTkFrame(row, fg_color="transparent")
            af.grid(row=0, column=2, sticky="e", padx=10)
            
            ctk.CTkButton(af, text="Edit",   width=60, height=28,
                command=lambda i=item: self.open_edit_modal(i)).pack(side="left", padx=5)
            
            ctk.CTkButton(af, text="Delete", width=60, height=28,
                fg_color="#d63031", hover_color="#b22828",
                command=lambda i=item: self.handle_delete(i)).pack(side="left")

    def open_add_modal(self):
        ItemModal(self, title_text="Add Password", on_save=self.save_new_item)
        
    def save_new_item(self, data):
        self.vault_service.add_item(self.session_data, data['title'], data['url'], data['username'], data['password'], data['notes'])
        self.refresh_list()

    def open_edit_modal(self, item):
        ItemModal(self, title_text="Edit Password", item_data=item, on_save=self.save_edit_item)
        
    def save_edit_item(self, data):
        self.vault_service.update_item(data['id'], self.session_data, data['title'], data['url'], data['username'], data['password'], data['notes'])
        self.refresh_list()

    def handle_delete(self, item):
        self.vault_service.delete_item(item['id'], self.session_data)
        self.refresh_list()

    def handle_logout(self):
        logger.info(f"User {self.session_data['username']} logged out.")
        self.session_data = None
        self.master.show_login_screen()
