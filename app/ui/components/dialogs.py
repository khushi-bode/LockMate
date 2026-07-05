import customtkinter as ctk

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
        x = master.winfo_rootx() + (master.winfo_width() // 2) - (self.winfo_width() // 2)
        y = master.winfo_rooty() + (master.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        color = "red" if is_error else "green"
        
        ctk.CTkLabel(self, text=message, text_color=color, wraplength=260).pack(expand=True, fill="both", padx=20, pady=20)
        
        ctk.CTkButton(self, text="OK", width=100, command=self.destroy).pack(pady=(0, 20))
