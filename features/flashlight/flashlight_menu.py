import customtkinter as ctk
from menu.custom_widgets.widgets import Widgets


class FlashlightMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#232323")

        self.enable_checkbox, _ = Widgets.render_checkbox(self, "Enable", False)
        self.flashlight_keybind, _ = Widgets.render_combobox(
            self, "Flashlight Keybind", ["M4", "M5", "MMB", "NONE"], "NONE"
        )

        # Hold threshold — LMB must be held this long before flashlight triggers
        hold_frame = ctk.CTkFrame(self, fg_color="transparent")
        hold_frame.pack(fill="x")
        self._hold_threshold_var = ctk.StringVar(value="50")
        self.hold_threshold_entry = ctk.CTkEntry(
            hold_frame,
            textvariable=self._hold_threshold_var,
            border_width=1,
            border_color="#404040",
            fg_color="#1A1A1A",
            text_color="#FFFFFF",
        )
        self.hold_threshold_entry.pack(padx=0, pady=3, fill="x", side="left")
        ctk.CTkLabel(
            hold_frame,
            text="Hold Threshold (ms)",
            font=ctk.CTkFont(size=12),
            text_color="#FFFFFF",
        ).pack(padx=3, pady=3, side="right")

        # Cooldown text input
        cooldown_frame = ctk.CTkFrame(self, fg_color="transparent")
        cooldown_frame.pack(fill="x")
        self._cooldown_var = ctk.StringVar(value="500")
        self.cooldown_entry = ctk.CTkEntry(
            cooldown_frame,
            textvariable=self._cooldown_var,
            border_width=1,
            border_color="#404040",
            fg_color="#1A1A1A",
            text_color="#FFFFFF",
        )
        self.cooldown_entry.pack(padx=0, pady=3, fill="x", side="left")
        ctk.CTkLabel(
            cooldown_frame,
            text="Cooldown (ms)",
            font=ctk.CTkFont(size=12),
            text_color="#FFFFFF",
        ).pack(padx=3, pady=3, side="right")

        # Pre-fire delay text input
        pre_fire_frame = ctk.CTkFrame(self, fg_color="transparent")
        pre_fire_frame.pack(fill="x")
        self._pre_fire_var = ctk.StringVar(value="15")
        self.pre_fire_entry = ctk.CTkEntry(
            pre_fire_frame,
            textvariable=self._pre_fire_var,
            border_width=1,
            border_color="#404040",
            fg_color="#1A1A1A",
            text_color="#FFFFFF",
        )
        self.pre_fire_entry.pack(padx=0, pady=3, fill="x", side="left")
        ctk.CTkLabel(
            pre_fire_frame,
            text="Pre-Fire Delay (ms)",
            font=ctk.CTkFont(size=12),
            text_color="#FFFFFF",
        ).pack(padx=3, pady=3, side="right")

    # ── Getters ──────────────────────────────────────────────────────────────

    def get_is_enabled(self) -> bool:
        return self.enable_checkbox.get()

    def get_flashlight_keybind(self) -> str:
        return self.flashlight_keybind.get()

    def get_hold_threshold(self) -> float:
        """Minimum time LMB must be held before flashlight triggers (seconds)."""
        try:
            value = float(self._hold_threshold_var.get().strip())
            return max(0.0, value) / 1000.0
        except ValueError:
            return 0.05  # safe default — 50ms

    def get_cooldown_ms(self) -> float:
        """Return the cooldown in seconds (converted from the ms text field)."""
        try:
            value = float(self._cooldown_var.get().strip())
            return max(0.0, value) / 1000.0
        except ValueError:
            return 0.5

    def get_pre_fire_delay(self) -> float:
        """Return the pre-fire delay in seconds (converted from the ms text field)."""
        try:
            value = float(self._pre_fire_var.get().strip())
            return max(0.0, value) / 1000.0
        except ValueError:
            return 0.015

    # ── Config persistence ────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return {
            "enabled":         self.enable_checkbox.get(),
            "keybind":         self.flashlight_keybind.get(),
            "hold_threshold_ms": self._hold_threshold_var.get(),
            "cooldown_ms":     self._cooldown_var.get(),
            "pre_fire_ms":     self._pre_fire_var.get(),
        }

    def load_config(self, data: dict) -> None:
        if "enabled" in data:
            if data["enabled"]:
                self.enable_checkbox.select()
            else:
                self.enable_checkbox.deselect()
        if "keybind" in data:
            self.flashlight_keybind.set(data["keybind"])
        if "hold_threshold_ms" in data:
            self._hold_threshold_var.set(data["hold_threshold_ms"])
        if "cooldown_ms" in data:
            self._cooldown_var.set(data["cooldown_ms"])
        if "pre_fire_ms" in data:
            self._pre_fire_var.set(data["pre_fire_ms"])
