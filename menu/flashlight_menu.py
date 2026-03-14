import customtkinter as ctk
import random
from menu.custom_widgets.widgets import Widgets


class FlashlightMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#232323")

        self.enable_checkbox, _ = Widgets.render_checkbox(self, "Master Enable", False)
        self.flashlight_keybind, _ = Widgets.render_combobox(
            self, "Flashlight Keybind", ["M4", "M5", "MMB", "NONE"], "NONE"
        )

        # Hold threshold
        hold_frame = ctk.CTkFrame(self, fg_color="transparent")
        hold_frame.pack(fill="x")
        self._hold_threshold_var = ctk.StringVar(value="50")
        self.hold_threshold_entry = ctk.CTkEntry(
            hold_frame, textvariable=self._hold_threshold_var,
            border_width=1, border_color="#404040", fg_color="#1A1A1A", text_color="#FFFFFF",
        )
        self.hold_threshold_entry.pack(padx=0, pady=3, fill="x", side="left")
        self._bind_validation(self.hold_threshold_entry, self._hold_threshold_var)
        ctk.CTkLabel(hold_frame, text="Hold Threshold (ms)", font=ctk.CTkFont(size=12), text_color="#FFFFFF").pack(padx=3, pady=3, side="right")

        # Cooldown
        cooldown_frame = ctk.CTkFrame(self, fg_color="transparent")
        cooldown_frame.pack(fill="x")
        self._cooldown_var = ctk.StringVar(value="500")
        self.cooldown_entry = ctk.CTkEntry(
            cooldown_frame, textvariable=self._cooldown_var,
            border_width=1, border_color="#404040", fg_color="#1A1A1A", text_color="#FFFFFF",
        )
        self.cooldown_entry.pack(padx=0, pady=3, fill="x", side="left")
        self._bind_validation(self.cooldown_entry, self._cooldown_var)
        ctk.CTkLabel(cooldown_frame, text="Cooldown (ms)", font=ctk.CTkFont(size=12), text_color="#FFFFFF").pack(padx=3, pady=3, side="right")

        # Pre-fire delay — Min and Max on one line, label on right to match other rows
        pre_fire_frame = ctk.CTkFrame(self, fg_color="transparent")
        pre_fire_frame.pack(fill="x")

        self._pre_fire_min_var = ctk.StringVar(value="15")
        self.pre_fire_min_entry = ctk.CTkEntry(
            pre_fire_frame, textvariable=self._pre_fire_min_var, width=55,
            border_width=1, border_color="#404040", fg_color="#1A1A1A", text_color="#FFFFFF",
        )
        self.pre_fire_min_entry.pack(side="left", padx=(0, 2), pady=3)
        self._bind_validation(self.pre_fire_min_entry, self._pre_fire_min_var)

        ctk.CTkLabel(pre_fire_frame, text="to", font=ctk.CTkFont(size=12), text_color="#888888").pack(side="left", padx=2, pady=3)

        self._pre_fire_max_var = ctk.StringVar(value="15")
        self.pre_fire_max_entry = ctk.CTkEntry(
            pre_fire_frame, textvariable=self._pre_fire_max_var, width=55,
            border_width=1, border_color="#404040", fg_color="#1A1A1A", text_color="#FFFFFF",
        )
        self.pre_fire_max_entry.pack(side="left", padx=(2, 0), pady=3)
        self._bind_validation(self.pre_fire_max_entry, self._pre_fire_max_var)

        ctk.CTkLabel(pre_fire_frame, text="Pre-Fire Delay (ms)", font=ctk.CTkFont(size=12), text_color="#FFFFFF").pack(side="right", padx=3, pady=3)

    # ── Input validation ─────────────────────────────────────────────────────

    def _bind_validation(self, entry: ctk.CTkEntry, var: ctk.StringVar) -> None:
        """Highlight entry red if value is not a valid non-negative number."""
        def _validate(*_):
            try:
                val = float(var.get().strip())
                color = "#404040" if val >= 0 else "#FF4444"
            except ValueError:
                color = "#FF4444"
            entry.configure(border_color=color)
        var.trace_add("write", _validate)

    # ── Getters ──────────────────────────────────────────────────────────────

    def get_is_enabled(self) -> bool:
        return self.enable_checkbox.get()

    def get_flashlight_keybind(self) -> str:
        return self.flashlight_keybind.get()

    def get_hold_threshold(self) -> float:
        try:
            return max(0.0, float(self._hold_threshold_var.get().strip())) / 1000.0
        except ValueError:
            return 0.05

    def get_cooldown_ms(self) -> float:
        try:
            return max(0.0, float(self._cooldown_var.get().strip())) / 1000.0
        except ValueError:
            return 0.5

    def get_pre_fire_delay(self) -> float:
        """Return a randomised delay between min and max (in seconds)."""
        try:
            min_ms = max(0.0, float(self._pre_fire_min_var.get().strip()))
        except ValueError:
            min_ms = 15.0
        try:
            max_ms = max(0.0, float(self._pre_fire_max_var.get().strip()))
        except ValueError:
            max_ms = 15.0

        # Ensure min <= max
        if min_ms > max_ms:
            min_ms, max_ms = max_ms, min_ms

        return random.uniform(min_ms, max_ms) / 1000.0

    # ── Config persistence ────────────────────────────────────────────────────

    def get_config(self) -> dict:
        return {
            "enabled":           self.enable_checkbox.get(),
            "keybind":           self.flashlight_keybind.get(),
            "hold_threshold_ms": self._hold_threshold_var.get(),
            "cooldown_ms":       self._cooldown_var.get(),
            "pre_fire_min_ms":   self._pre_fire_min_var.get(),
            "pre_fire_max_ms":   self._pre_fire_max_var.get(),
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
        # Support old single pre_fire_ms key — load into both min and max
        if "pre_fire_ms" in data:
            self._pre_fire_min_var.set(data["pre_fire_ms"])
            self._pre_fire_max_var.set(data["pre_fire_ms"])
        if "pre_fire_min_ms" in data:
            self._pre_fire_min_var.set(data["pre_fire_min_ms"])
        if "pre_fire_max_ms" in data:
            self._pre_fire_max_var.set(data["pre_fire_max_ms"])
