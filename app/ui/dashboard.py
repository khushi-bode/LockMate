import customtkinter as ctk
from app.utils.logger import logger
from app.core.vault_service import VaultService
from app.ui.components.item_modal import ItemModal
from app.ui.components.dialogs import ConfirmDialog, MessageDialog
from app.ui.password_generator import PasswordGeneratorScreen
from app.ui.settings import SettingsScreen
import config


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, session_data: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.session_data = session_data
        self.vault_service = VaultService()

        from app.data.user_repository import UserRepository

        self.user_repo = UserRepository()
        self.expired_ids = set()

        self.active_panel = None

        # Configure layout (2 columns: Sidebar, Main Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.show_vault_panel()  # Default view

        logger.info(
            f"Dashboard screen displayed for user: {self.session_data['username']}"
        )

    # ─────────────────────────────────────────
    #  Sidebar
    # ─────────────────────────────────────────
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(
            self, width=config.SIDEBAR_WIDTH, corner_radius=0
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Spacer pushes logout down

        # App logo / title
        ctk.CTkLabel(
            self.sidebar_frame,
            text=config.APP_TITLE,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 30))

        # Navigation definitions: (label, callback)
        nav_items = [
            ("All Items", self.show_vault_panel),
            ("Password Generator", self.show_generator_panel),
            ("Settings", self.show_settings_panel),
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
                command=callback,
            )
            btn.grid(row=idx + 1, column=0, padx=20, pady=10, sticky="ew")
            self.nav_buttons.append(btn)

        # Lock Vault button
        self.logout_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Lock Vault Now",
            fg_color="#d63031",
            hover_color="#b22828",
            command=self.handle_logout,
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
            font=ctk.CTkFont(size=32, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=40, pady=(40, 10))

        # Warning Banner (Hidden by default)
        self.warning_frame = ctk.CTkFrame(parent, fg_color="#d63031", corner_radius=8)
        self.warning_label = ctk.CTkLabel(
            self.warning_frame,
            text="",
            text_color="white",
            font=ctk.CTkFont(weight="bold"),
        )
        self.warning_label.pack(pady=10, padx=20)

        # Stats Cards
        self.stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.stats_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))

        # We will populate them in refresh_list
        self.stat_total = self.create_stat_card(
            self.stats_frame, "Total Passwords", "0"
        )
        self.stat_fav = self.create_stat_card(
            self.stats_frame, "Favorite Passwords", "0"
        )
        self.stat_weak = self.create_stat_card(self.stats_frame, "Weak Passwords", "0")
        self.stat_strong = self.create_stat_card(
            self.stats_frame, "Strong Passwords", "0"
        )

        # Search + Add button row
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 20))

        self.search_entry = ctk.CTkEntry(
            actions_frame, placeholder_text="Search vault...", width=300
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.handle_search)

        self.filter_var = ctk.StringVar(value="All")
        self.filter_seg = ctk.CTkSegmentedButton(
            actions_frame,
            values=["All", "Favorites", "Expired"],
            variable=self.filter_var,
            command=self.handle_filter,
        )
        self.filter_seg.pack(side="left", padx=20)

        self.cat_filter_var = ctk.StringVar(value="All Categories")
        self.cat_filter = ctk.CTkOptionMenu(
            actions_frame,
            values=[
                "All Categories",
                "Personal",
                "Work",
                "Banking",
                "Social",
                "Shopping",
                "Entertainment",
                "Other",
            ],
            variable=self.cat_filter_var,
            command=self.handle_filter,
        )
        self.cat_filter.pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            actions_frame, text="+ Add Password", command=self.open_add_modal
        ).pack(side="right")

        # Column headers
        header = ctk.CTkFrame(parent, fg_color=("gray85", "gray25"), corner_radius=5)
        header.grid(row=4, column=0, sticky="ew", padx=40, pady=(0, 5))
        header.grid_columnconfigure(0, weight=2)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=2)
        header.grid_columnconfigure(3, weight=2)
        header.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(header, text="Title", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, sticky="w", padx=10, pady=5
        )
        ctk.CTkLabel(header, text="Category", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=1, sticky="w", padx=10, pady=5
        )
        ctk.CTkLabel(header, text="Username", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=2, sticky="w", padx=10, pady=5
        )
        ctk.CTkLabel(header, text="Password", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=3, sticky="w", padx=10, pady=5
        )
        ctk.CTkLabel(header, text="Actions", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=4, sticky="e", padx=10, pady=5
        )

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.list_frame.grid(row=5, column=0, sticky="nsew", padx=40, pady=(0, 40))

        self.refresh_list()

    def create_stat_card(self, parent, title, value):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(side="left", expand=True, fill="both", padx=(0, 10))

        title_label = ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=12), text_color="gray"
        )
        title_label.pack(pady=(15, 5), padx=15)

        value_label = ctk.CTkLabel(
            card, text=value, font=ctk.CTkFont(size=24, weight="bold")
        )
        value_label.pack(pady=(0, 15), padx=15)
        return value_label

    # ─────────────────────────────────────────
    #  Vault CRUD
    # ─────────────────────────────────────────
    def handle_search(self, event=None):
        query = self.search_entry.get().strip()
        logger.info(f"Dashboard: Search triggered with query '{query}'")
        self.refresh_list()

    def handle_filter(self, value):
        logger.info(f"Dashboard: Filter changed to '{value}'")
        self.refresh_list()

    def update_stats(self):
        if hasattr(self, "stat_total"):
            health = self.vault_service.get_vault_health(self.session_data)
            self.stat_total.configure(text=str(health["total"]))
            self.stat_fav.configure(text=str(health["favorites"]))
            self.stat_weak.configure(
                text=str(health["weak"]),
                text_color="#d63031" if health["weak"] > 0 else "gray90",
            )
            self.stat_strong.configure(
                text=str(health["strong"]),
                text_color="#00b894" if health["strong"] > 0 else "gray90",
            )

    def refresh_list(self):
        self.revealed_pw_label = None

        # Calculate expired items
        from datetime import datetime

        now = datetime.utcnow()
        self.expired_ids = set()

        settings = self.user_repo.get_user_settings(self.session_data["user_id"])
        expiry_days = settings.get("expiry_days", 0)

        all_items = self.vault_service.get_all_items(self.session_data)

        if expiry_days > 0:
            for i in all_items:
                dt_str = i.get("updated_at") or i.get("created_at")
                if dt_str:
                    try:
                        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        if (now - dt).days >= expiry_days:
                            self.expired_ids.add(i["id"])
                    except Exception:
                        pass

        if hasattr(self, "warning_frame"):
            if self.expired_ids:
                self.warning_label.configure(
                    text=f"Warning: You have {len(self.expired_ids)} expired password(s)!"
                )
                self.warning_frame.grid(
                    row=1, column=0, sticky="ew", padx=40, pady=(0, 20)
                )
            else:
                self.warning_frame.grid_forget()

        query = self.search_entry.get().strip()
        filter_val = getattr(self, "filter_var", None)
        show_favs = filter_val and filter_val.get() == "Favorites"
        show_exp = filter_val and filter_val.get() == "Expired"

        cat_val = getattr(self, "cat_filter_var", None)
        selected_cat = cat_val.get() if cat_val else "All Categories"

        if show_favs:
            items = self.vault_service.get_favorites(self.session_data)
        else:
            if query:
                items = self.vault_service.search_items(self.session_data, query)
            else:
                items = all_items

        filtered_items = []
        for i in items:
            if (
                selected_cat != "All Categories"
                and i.get("category", "Other") != selected_cat
            ):
                continue
            if show_exp and i["id"] not in self.expired_ids:
                continue
            if show_favs and query:
                q = query.lower()
                if (
                    q not in i["title"].lower()
                    and q not in i.get("username", "").lower()
                    and q not in i.get("url", "").lower()
                ):
                    continue
            filtered_items.append(i)

        items = filtered_items

        # Update health stats
        self.update_stats()

        self.render_items(items, is_search=bool(query))

    def render_items(self, items, is_search=False):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not items:
            msg = (
                "No matching passwords found."
                if is_search
                else "No items found in vault."
            )
            ctk.CTkLabel(self.list_frame, text=msg, text_color="gray").pack(pady=20)
            return

        for idx, item in enumerate(items):
            is_expired = item["id"] in self.expired_ids
            bg_color = (
                ("#ffcccc", "#4a1c1c")
                if is_expired
                else (("gray95", "gray15") if idx % 2 == 0 else ("gray90", "gray10"))
            )

            row = ctk.CTkFrame(self.list_frame, fg_color=bg_color, corner_radius=0)
            row.pack(fill="x", pady=2)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=2)
            row.grid_columnconfigure(3, weight=2)
            row.grid_columnconfigure(4, weight=1)

            star_text = "★" if item.get("is_favorite") == 1 else "☆"
            star_color = "#f1c40f" if item.get("is_favorite") == 1 else "gray"

            star_btn = ctk.CTkButton(
                row,
                text=star_text,
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
                text_color=star_color,
                font=ctk.CTkFont(size=20),
            )
            star_btn.configure(
                command=lambda i=item, b=star_btn, r=row: self.toggle_favorite(i, b, r)
            )
            star_btn.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=10)

            ctk.CTkLabel(row, text=item["title"]).grid(
                row=0, column=0, sticky="w", padx=(50, 10), pady=10
            )
            ctk.CTkLabel(row, text=item.get("category", "Other")).grid(
                row=0, column=1, sticky="w", padx=10, pady=10
            )

            un_frame = ctk.CTkFrame(row, fg_color="transparent")
            un_frame.grid(row=0, column=2, sticky="w", padx=10, pady=10)

            ctk.CTkLabel(un_frame, text=item.get("username", "")).pack(
                side="left", padx=(0, 5)
            )

            copy_un_btn = ctk.CTkButton(
                un_frame,
                text="📋",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
            )
            copy_un_btn.configure(
                command=lambda u=item.get("username", ""): self.copy_to_clipboard(
                    u, "Username copied"
                )
            )
            copy_un_btn.pack(side="left")

            pw_frame = ctk.CTkFrame(row, fg_color="transparent")
            pw_frame.grid(row=0, column=3, sticky="w", padx=10, pady=10)

            pw_label = ctk.CTkLabel(pw_frame, text="••••••••", text_color="gray")
            pw_label.pack(side="left", padx=(0, 5))

            eye_btn = ctk.CTkButton(
                pw_frame,
                text="👁",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
            )
            eye_btn.configure(
                command=lambda i=item, lbl=pw_label: self.toggle_row_password(i, lbl)
            )
            eye_btn.pack(side="left")

            copy_pw_btn = ctk.CTkButton(
                pw_frame,
                text="📋",
                width=30,
                height=28,
                fg_color="transparent",
                hover_color=("gray80", "gray20"),
            )
            copy_pw_btn.configure(
                command=lambda p=item.get("password", ""): self.copy_to_clipboard(
                    p, "Password copied"
                )
            )
            copy_pw_btn.pack(side="left")

            af = ctk.CTkFrame(row, fg_color="transparent")
            af.grid(row=0, column=4, sticky="e", padx=10)

            ctk.CTkButton(
                af,
                text="Edit",
                width=60,
                height=28,
                command=lambda i=item: self.open_edit_modal(i),
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                af,
                text="Delete",
                width=60,
                height=28,
                fg_color="#d63031",
                hover_color="#b22828",
                command=lambda i=item: self.handle_delete(i),
            ).pack(side="left")

    def copy_to_clipboard(self, value, message):
        self.clipboard_clear()
        if value:
            self.clipboard_append(value)
        MessageDialog(self, title="Success", message=message)

    def toggle_row_password(self, item, pw_label):
        # If clicking the currently revealed one, hide it
        if getattr(self, "revealed_pw_label", None) == pw_label:
            pw_label.configure(text="••••••••")
            self.revealed_pw_label = None
            return

        # Hide the previously revealed one
        if getattr(self, "revealed_pw_label", None):
            self.revealed_pw_label.configure(text="••••••••")

        # Reveal the new one
        pw_label.configure(text=item.get("password", ""))
        self.revealed_pw_label = pw_label

    def toggle_favorite(self, item, star_btn, row_frame):
        success = self.vault_service.toggle_favorite(item["id"], self.session_data)
        if success:
            item["is_favorite"] = 1 if item.get("is_favorite", 0) == 0 else 0

            star_text = "★" if item["is_favorite"] == 1 else "☆"
            star_color = "#f1c40f" if item["is_favorite"] == 1 else "gray"
            star_btn.configure(text=star_text, text_color=star_color)

            filter_val = getattr(self, "filter_var", None)
            if (
                filter_val
                and filter_val.get() == "Favorites"
                and item["is_favorite"] == 0
            ):
                row_frame.destroy()

            self.update_stats()
            MessageDialog(self, title="Success", message="Favorite status updated.")

    def open_add_modal(self):
        ItemModal(self, title_text="Add Password", on_save=self.save_new_item)

    def save_new_item(self, data):
        self.vault_service.add_item(
            self.session_data,
            data["title"],
            data["url"],
            data["username"],
            data["password"],
            data["notes"],
            data.get("category", "Other"),
        )
        self.refresh_list()

    def open_edit_modal(self, item):
        ItemModal(
            self,
            title_text="Edit Password",
            item_data=item,
            on_save=self.save_edit_item,
        )

    def save_edit_item(self, data):
        logger.info(f"Dashboard: Saving edit for item ID {data.get('id')}")
        self.vault_service.update_item(
            data["id"],
            self.session_data,
            data["title"],
            data["url"],
            data["username"],
            data["password"],
            data["notes"],
            data.get("category", "Other"),
        )
        self.refresh_list()

    def handle_delete(self, item):
        logger.info(f"Dashboard: Delete requested for item ID {item['id']}")

        def on_confirm():
            logger.info(f"Dashboard: Delete confirmed for item ID {item['id']}")
            success = self.vault_service.delete_item(item["id"], self.session_data)
            if success:
                self.refresh_list()
                MessageDialog(
                    self, title="Success", message="Password deleted successfully."
                )
            else:
                MessageDialog(
                    self,
                    title="Error",
                    message="Failed to delete password.",
                    is_error=True,
                )

        def on_cancel():
            logger.info(f"Dashboard: Delete cancelled for item ID {item['id']}")

        ConfirmDialog(
            self,
            title="Delete Password",
            message=f"Are you sure you want to delete '{item['title']}'? This action cannot be undone.",
            on_confirm=on_confirm,
            on_cancel=on_cancel,
        )

    def handle_logout(self):
        logger.info("Manual vault lock initiated.")
        logger.info("Session cleared.")

        # Close any sensitive dialogs
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                widget.destroy()

        # Hide any visible passwords by resetting state
        self.revealed_pw_label = None

        # Clear clipboard if it contains passwords
        try:
            self.clipboard_clear()
        except Exception:
            pass

        self.session_data = None

        logger.info("Login screen restored.")
        self.master.show_login_screen()
