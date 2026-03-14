import customtkinter as ctk

from menu.custom_widgets.widgets import Widgets
from menu.games import ALL_GAMES


class SettingsMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.configure(fg_color="transparent")

        ctk.CTkLabel(self, text="Game", text_color="#FFFFFF").pack(padx=3, pady=(5, 0), anchor="w")
        self.game_scaler = ctk.CTkComboBox(
            self,
            values=ALL_GAMES,
            border_width=1,
            border_color="#404040",
            button_color="#1A1A1A",
            fg_color="#1A1A1A",
            text_color="#FFFFFF",
        )
        self.game_scaler.set("Manual")
        self.game_scaler.pack(padx=3, pady=(0, 5), fill="x")

        ctk.CTkLabel(self, text="In-Game Sensitivity", text_color="#FFFFFF").pack(padx=3, pady=(5, 0), anchor="w")
        self.sensitivity_input = ctk.CTkTextbox(self, height=20, border_width=1, border_color="#404040", fg_color="#1A1A1A", text_color="#FFFFFF")
        self.sensitivity_input.pack(padx=3, pady=(0, 3), fill="x")

    def get_game_sensitivity(self) -> float:
        """Return the user's current in-game sensitivity. Defaults to 1.0 if empty or invalid."""
        try:
            value = self.sensitivity_input.get("1.0", "end").strip()
            sens = float(value)
            return sens if sens > 0 else 1.0
        except ValueError:
            return 1.0

    def get_game_scalar(self) -> str:
        return str(self.game_scaler.get())

    # ── Config persistence ────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return {
            "game_scalar":      self.game_scaler.get(),
            "game_sensitivity": self.sensitivity_input.get("1.0", "end").strip(),
        }

    def load_config(self, data: dict) -> None:
        if "game_scalar" in data:
            self.game_scaler.set(data["game_scalar"])
        # Support old key name (cs2_sensitivity) for backwards compatibility
        sensitivity = data.get("game_sensitivity") or data.get("cs2_sensitivity", "")
        if sensitivity:
            self.sensitivity_input.delete("1.0", "end")
            self.sensitivity_input.insert("1.0", sensitivity)
