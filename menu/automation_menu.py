import customtkinter as ctk
from tkinter import filedialog


class AutomationMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x")
        ctk.CTkLabel(info_frame, text="Format: X, Y, MS_DELAY, EVENT", font=ctk.CTkFont(size=12)).pack(padx=5, pady=1, side="left")
        ctk.CTkLabel(info_frame, text="Events: RCLICK, LCLICK", font=ctk.CTkFont(size=12)).pack(padx=5, pady=1, side="right")

        self.mouse_movements_inpt = ctk.CTkTextbox(self, width=150, height=250, font=("Consolas", 14), border_width=1, border_color="gray")
        self.mouse_movements_inpt.pack(padx=5, pady=5, fill="x")
        self.mouse_movements_inpt.bind("<<Modified>>", self.on_modified)

    def on_modified(self, _=None):
        self.mouse_movements_inpt.edit_modified(False)

    def get_script_text(self):
        return self.mouse_movements_inpt.get("0.0", "end-1c")

    def get_config(self) -> dict:
        return {
            "script": self.get_script_text(),
        }

    def load_config(self, data: dict) -> None:
        script = data.get("script", "")
        if script:
            self.mouse_movements_inpt.delete("0.0", "end")
            self.mouse_movements_inpt.insert("0.0", script)
