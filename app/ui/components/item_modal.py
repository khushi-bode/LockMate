import customtkinter as ctk


class ItemModal(ctk.CTkToplevel):
    def __init__(self, master, title_text, item_data=None, on_save=None, **kwargs):
        super().__init__(master, **kwargs)

        self.title(title_text)
        self.geometry("400x550")
        self.resizable(False, False)

        # Make modal block the main window
        self.transient(master)
        self.grab_set()

        self.item_data = item_data or {}
        self.on_save = on_save

        self.create_widgets()

        # Center the modal relative to master
        self.update_idletasks()
        x = (
            master.winfo_rootx()
            + (master.winfo_width() // 2)
            - (self.winfo_width() // 2)
        )
        y = (
            master.winfo_rooty()
            + (master.winfo_height() // 2)
            - (self.winfo_height() // 2)
        )
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=30, pady=20)

        # Title Field
        ctk.CTkLabel(frame, text="Title*", anchor="w").pack(fill="x")
        self.title_entry = ctk.CTkEntry(frame)
        self.title_entry.pack(fill="x", pady=(0, 15))
        self.title_entry.insert(0, self.item_data.get("title", ""))

        # URL Field
        ctk.CTkLabel(frame, text="URL", anchor="w").pack(fill="x")
        self.url_entry = ctk.CTkEntry(frame)
        self.url_entry.pack(fill="x", pady=(0, 15))
        self.url_entry.insert(0, self.item_data.get("url", ""))

        # Username Field
        ctk.CTkLabel(frame, text="Username", anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(frame)
        self.username_entry.pack(fill="x", pady=(0, 15))
        self.username_entry.insert(0, self.item_data.get("username", ""))

        # Password Field
        ctk.CTkLabel(frame, text="Password*", anchor="w").pack(fill="x")

        pw_frame = ctk.CTkFrame(frame, fg_color="transparent")
        pw_frame.pack(fill="x")

        self.password_entry = ctk.CTkEntry(pw_frame, show="*")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.password_entry.insert(0, self.item_data.get("password", ""))

        self.show_btn = ctk.CTkButton(
            pw_frame, text="Show", width=50, command=self.toggle_pw
        )
        self.show_btn.pack(side="left", padx=(0, 10))

        self.gen_btn = ctk.CTkButton(
            pw_frame, text="Generate", width=70, command=self.open_generator
        )
        self.gen_btn.pack(side="left")

        self.strength_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.strength_frame.pack(fill="x", pady=(5, 15))

        self.strength_bar = ctk.CTkProgressBar(self.strength_frame, height=8)
        self.strength_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.strength_bar.set(0)

        self.strength_label = ctk.CTkLabel(
            self.strength_frame,
            text="None",
            font=ctk.CTkFont(size=12),
            width=70,
            anchor="e",
        )
        self.strength_label.pack(side="right")

        self.password_entry.bind("<KeyRelease>", self.update_strength)

        from app.core.password_generator import PasswordGeneratorService

        self.pwd_service = PasswordGeneratorService()
        self.update_strength()

        # Category Field
        ctk.CTkLabel(frame, text="Category", anchor="w").pack(fill="x")
        self.category_var = ctk.StringVar(value=self.item_data.get("category", "Other"))
        self.category_menu = ctk.CTkOptionMenu(
            frame,
            values=[
                "Personal",
                "Work",
                "Banking",
                "Social",
                "Shopping",
                "Entertainment",
                "Other",
            ],
            variable=self.category_var,
        )
        self.category_menu.pack(fill="x", pady=(0, 15))

        # Notes Field
        ctk.CTkLabel(frame, text="Notes", anchor="w").pack(fill="x")
        self.notes_textbox = ctk.CTkTextbox(frame, height=80)
        self.notes_textbox.pack(fill="x", pady=(0, 20))
        if self.item_data.get("notes"):
            self.notes_textbox.insert("1.0", self.item_data["notes"])

        # Error Label
        self.error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.error_label.pack(pady=(0, 10))

        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=self.destroy,
        ).pack(side="left", expand=True, padx=(0, 10))

        ctk.CTkButton(btn_frame, text="Save", command=self.handle_save).pack(
            side="left", expand=True, padx=(10, 0)
        )

    def toggle_pw(self):
        if self.password_entry.cget("show") == "*":
            self.password_entry.configure(show="")
            self.show_btn.configure(text="Hide")
        else:
            self.password_entry.configure(show="*")
            self.show_btn.configure(text="Show")

    def update_strength(self, event=None):
        pw = self.password_entry.get()
        label, color, score = self.pwd_service.calculate_strength(pw)
        self.strength_bar.set(score)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=label, text_color=color)

    def open_generator(self):
        from app.ui.components.dialogs import GeneratorDialog

        def on_use(pw):
            self.password_entry.delete(0, "end")
            self.password_entry.insert(0, pw)
            if self.password_entry.cget("show") == "*":
                self.toggle_pw()
            self.update_strength()

        GeneratorDialog(self, on_use_password=on_use)

    def handle_save(self):
        title = self.title_entry.get().strip()
        password = self.password_entry.get().strip()

        if not title or not password:
            self.error_label.configure(text="Title and Password are required.")
            return

        data = {
            "title": title,
            "url": self.url_entry.get().strip(),
            "username": self.username_entry.get().strip(),
            "password": password,
            "notes": self.notes_textbox.get("1.0", "end-1c").strip(),
            "category": self.category_var.get(),
        }

        if self.item_data.get("id"):
            data["id"] = self.item_data["id"]

        if self.on_save:
            self.on_save(data)

        self.destroy()
