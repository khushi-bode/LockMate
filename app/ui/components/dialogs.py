import customtkinter as ctk
from app.core.password_generator import PasswordGeneratorService
from app.utils.logger import logger


class MessageDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Message", message="", is_error=False, **kwargs):
        super().__init__(master, **kwargs)

        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Center
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

        color = "red" if is_error else "green"

        ctk.CTkLabel(self, text=message, text_color=color, wraplength=260).pack(
            expand=True, fill="both", padx=20, pady=20
        )

        ctk.CTkButton(self, text="OK", width=100, command=self.destroy).pack(
            pady=(0, 20)
        )


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        title="Confirm",
        message="Are you sure?",
        on_confirm=None,
        on_cancel=None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

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

        ctk.CTkLabel(self, text=message, wraplength=260).pack(
            expand=True, fill="both", padx=20, pady=20
        )

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 20), padx=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            command=self.handle_cancel,
        ).pack(side="left", expand=True, padx=(0, 5))
        ctk.CTkButton(
            btn_frame,
            text="Confirm",
            fg_color="#d63031",
            hover_color="#b22828",
            command=self.handle_confirm,
        ).pack(side="right", expand=True, padx=(5, 0))

    def handle_confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.destroy()

    def handle_cancel(self):
        if self.on_cancel:
            self.on_cancel()
        self.destroy()


class GeneratorDialog(ctk.CTkToplevel):
    def __init__(self, master, on_use_password=None, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Password Generator")
        self.geometry("400x500")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.on_use_password = on_use_password
        self.generator = PasswordGeneratorService()

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

        self.create_widgets()
        self.generate()

    def create_widgets(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=30, pady=20)

        self.output_var = ctk.StringVar()
        self.output_entry = ctk.CTkEntry(
            frame,
            textvariable=self.output_var,
            font=ctk.CTkFont(size=20),
            justify="center",
            state="readonly",
        )
        self.output_entry.pack(fill="x", pady=(0, 20), ipady=10)

        len_frame = ctk.CTkFrame(frame, fg_color="transparent")
        len_frame.pack(fill="x", pady=(0, 20))

        self.len_val = ctk.IntVar(value=16)
        self.len_label = ctk.CTkLabel(len_frame, text=f"Length: {self.len_val.get()}")
        self.len_label.pack(side="top", anchor="w")

        self.len_slider = ctk.CTkSlider(
            len_frame,
            from_=8,
            to=64,
            variable=self.len_val,
            command=self.update_len_label,
        )
        self.len_slider.pack(fill="x")

        self.var_upper = ctk.BooleanVar(value=True)
        self.var_lower = ctk.BooleanVar(value=True)
        self.var_digits = ctk.BooleanVar(value=True)
        self.var_symbols = ctk.BooleanVar(value=True)

        ctk.CTkCheckBox(
            frame,
            text="Uppercase (A-Z)",
            variable=self.var_upper,
            command=self.generate,
        ).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(
            frame,
            text="Lowercase (a-z)",
            variable=self.var_lower,
            command=self.generate,
        ).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(
            frame, text="Numbers (0-9)", variable=self.var_digits, command=self.generate
        ).pack(anchor="w", pady=5)
        ctk.CTkCheckBox(
            frame,
            text="Symbols (!@#$)",
            variable=self.var_symbols,
            command=self.generate,
        ).pack(anchor="w", pady=5)

        action_frame = ctk.CTkFrame(frame, fg_color="transparent")
        action_frame.pack(fill="x", pady=(30, 0))

        ctk.CTkButton(action_frame, text="Copy", command=self.copy_to_clipboard).pack(
            side="left", expand=True, padx=5
        )
        ctk.CTkButton(action_frame, text="Regenerate", command=self.generate).pack(
            side="left", expand=True, padx=5
        )

        if self.on_use_password:
            ctk.CTkButton(
                action_frame,
                text="Use Password",
                command=self.use_password,
                fg_color="#00b894",
                hover_color="#00a884",
            ).pack(side="left", expand=True, padx=5)

    def update_len_label(self, val):
        self.len_label.configure(text=f"Length: {int(val)}")
        self.generate()

    def generate(self, *_):
        length = self.len_val.get()
        pw = self.generator.generate(
            length=length,
            use_lower=self.var_lower.get(),
            use_upper=self.var_upper.get(),
            use_digits=self.var_digits.get(),
            use_symbols=self.var_symbols.get(),
        )
        self.output_var.set(pw)
        logger.info("PasswordGenerator: Password generated.")

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_var.get())
        logger.info("PasswordGenerator: Password copied to clipboard.")

    def use_password(self):
        if self.on_use_password:
            self.on_use_password(self.output_var.get())
        self.destroy()
