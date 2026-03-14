import customtkinter as ctk
import threading
import time

from .automation_menu import AutomationMenu
from .recoil_menu import RecoilMenu
from .settings_menu import SettingsMenu
from .flashlight_menu import FlashlightMenu

from customtkinter import CTkImage
from PIL import Image

import os
import sys


class MenuApp(ctk.CTk):
    def __init__(self):
        self.is_running = True

        super().__init__()
        self.geometry("400x880")
        ctk.set_default_color_theme("dark-blue")
        ctk.set_widget_scaling(0.8)

        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
            EXE_DIR = os.path.dirname(sys.executable)
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            EXE_DIR = BASE_DIR

        logo_path = os.path.join(EXE_DIR, "assets", "logo.png")

        self.title("")
        self.resizable(False, False)
        self.configure(fg_color="#151515")

        logo = Image.open(logo_path)
        logo = logo.resize((120, 120))
        logo_image = CTkImage(light_image=logo, dark_image=logo, size=(120, 120))
        ctk.CTkLabel(self, image=logo_image, text="").pack(pady=(7, 0))

        # Makcu connection status indicator — hidden by default, shown on connect
        self.status_label = ctk.CTkLabel(
            self,
            text="● Makcu Connected",
            font=ctk.CTkFont(size=11),
            text_color="#44FF77",
        )
        self.status_label.pack(pady=(0, 6))
        self.status_label.configure(text="")  # hide until connected

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

    def set_makcu_connected(self):
        """Flash 'Makcu Connected' green slowly for 10 seconds then hide it."""
        def _flash():
            end_time = time.monotonic() + 10.0
            visible = True
            while time.monotonic() < end_time:
                text = "● Makcu Connected" if visible else ""
                color = "#44FF77"
                try:
                    self.status_label.configure(text=text, text_color=color)
                except Exception:
                    return
                visible = not visible
                time.sleep(0.8)  # 0.8s on/off — slow relaxed flash
            # Hide after 10 seconds
            try:
                self.status_label.configure(text="")
            except Exception:
                pass

        threading.Thread(target=_flash, daemon=True).start()

    def set_makcu_disconnected(self):
        """Show a persistent red disconnected label."""
        try:
            self.status_label.configure(text="● Makcu Not Connected", text_color="#FF4444")
        except Exception:
            pass
