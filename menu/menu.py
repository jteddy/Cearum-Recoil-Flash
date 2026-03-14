import customtkinter as ctk
import threading
import time

from .recoil_menu import RecoilMenu
from .settings_menu import SettingsMenu
from .flashlight_menu import FlashlightMenu

from customtkinter import CTkImage
from PIL import Image

import os
import sys

VERSION = "V1.0.6 F0.1"


class MenuApp(ctk.CTk):
    def __init__(self):
        self.is_running = True

        super().__init__()
        self.geometry("400x920")
        ctk.set_default_color_theme("dark-blue")
        ctk.set_widget_scaling(0.8)

        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
            EXE_DIR = os.path.dirname(sys.executable)
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            EXE_DIR = os.path.dirname(BASE_DIR)

        logo_path = os.path.join(EXE_DIR, "assets", "logo.png")

        self.title("")
        self.resizable(False, False)
        self.configure(fg_color="#151515")

        logo = Image.open(logo_path)
        logo = logo.resize((120, 120))
        logo_image = CTkImage(light_image=logo, dark_image=logo, size=(120, 120))
        ctk.CTkLabel(self, image=logo_image, text="").pack(pady=(7, 0))

        # Makcu connection status — flashes on connect then disappears
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#44FF77",
        )
        self.status_label.pack(pady=(0, 2))

        # Recoil / Flashlight status bar — always visible
        status_bar = ctk.CTkFrame(self, fg_color="transparent")
        status_bar.pack(pady=(0, 0))

        self.recoil_status_label = ctk.CTkLabel(
            status_bar,
            text="● Recoil: OFF",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        self.recoil_status_label.pack(side="left", padx=(0, 16))

        self.flashlight_status_label = ctk.CTkLabel(
            status_bar,
            text="● Flashlight: OFF",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        self.flashlight_status_label.pack(side="left")

        # Version label — bottom right of header
        ctk.CTkLabel(
            self,
            text=VERSION,
            font=ctk.CTkFont(size=9),
            text_color="#444444",
        ).pack(anchor="e", padx=10, pady=(0, 2))

        self.tabs = ctk.CTkTabview(
            self, width=280, height=340, border_width=1,
            fg_color="#232323", border_color="#404040"
        )
        self.tabs.pack(padx=10, pady=(0, 0), fill="both", expand=True)

        self.mouse_tab = self.tabs.add("Recoil")
        self.flashlight_tab = self.tabs.add("Flashlight")
        self.settings_tab = self.tabs.add("Settings")

        self.recoil_menu = RecoilMenu(self.mouse_tab)
        self.recoil_menu.pack(padx=5, pady=5, fill="both", expand=True)

        self.flashlight_menu = FlashlightMenu(self.flashlight_tab)
        self.flashlight_menu.pack(padx=5, pady=5, fill="both", expand=True)

        self.settings_menu = SettingsMenu(self.settings_tab)
        self.settings_menu.pack(padx=5, pady=5, fill="both", expand=True)

    def start_status_polling(self):
        """Poll recoil and flashlight states every 200ms, scheduling UI updates safely on main thread."""
        def _poll():
            while True:
                try:
                    recoil_on = self.recoil_menu.get_is_enabled()
                    # Flashlight is truly active only when master enable AND recoil are both on
                    flashlight_active = self.flashlight_menu.get_is_enabled() and recoil_on
                    self.after(0, lambda r=recoil_on, f=flashlight_active: self._update_status_labels(r, f))
                except Exception:
                    pass
                time.sleep(0.2)

        threading.Thread(target=_poll, daemon=True).start()

    def _update_status_labels(self, recoil_on: bool, flashlight_on: bool):
        """Called on the main thread — safe to update tkinter widgets."""
        try:
            self.recoil_status_label.configure(
                text="● Recoil: ON" if recoil_on else "● Recoil: OFF",
                text_color="#44FF77" if recoil_on else "#888888",
            )
            self.flashlight_status_label.configure(
                text="● Flashlight: ON" if flashlight_on else "● Flashlight: OFF",
                text_color="#44FF77" if flashlight_on else "#888888",
            )
        except Exception:
            pass

    def set_makcu_connected(self):
        """Flash Makcu Connected green for 10 seconds then hide."""
        def _flash():
            end_time = time.monotonic() + 10.0
            visible = True
            while time.monotonic() < end_time:
                text = "● Makcu Connected" if visible else ""
                try:
                    self.after(0, lambda t=text: self.status_label.configure(text=t, text_color="#44FF77"))
                except Exception:
                    return
                visible = not visible
                time.sleep(0.8)
            try:
                self.after(0, lambda: self.status_label.configure(text=""))
            except Exception:
                pass

        threading.Thread(target=_flash, daemon=True).start()

    def set_makcu_disconnected(self):
        try:
            self.after(0, lambda: self.status_label.configure(text="● Makcu Not Connected", text_color="#FF4444"))
        except Exception:
            pass
