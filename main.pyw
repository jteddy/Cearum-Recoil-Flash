from menu.menu import MenuApp
from mouse.makcu import makcu_controller
from features.recoil.recoil import recoil
from features.flashlight.flashlight import flashlight
from menu import config_manager

import tkinter as tk
from tkinter import messagebox

import time
import threading
import os


def show_error(title: str, message: str):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showerror(title, message)


def main():
    app = MenuApp()

    # Restore all settings from the previous session
    config_manager.load(app.recoil_menu, app.flashlight_menu, app.settings_menu)

    if makcu_controller.connect() is None:
        app.set_makcu_disconnected()
        show_error("Cearum", "There was an error connecting to your Makcu. Please make sure it's connected and try again.")
        time.sleep(3)
        return

    app.set_makcu_connected()
    makcu_controller.StartButtonListener()
    app.start_status_polling()

    recoil_thread = threading.Thread(
        target=recoil.run_recoil,
        args=(app.recoil_menu, app.settings_menu),
        daemon=True
    )
    recoil_thread.start()

    flashlight_thread = threading.Thread(
        target=flashlight.run_flashlight,
        args=(app.flashlight_menu, app.recoil_menu),
        daemon=True
    )
    flashlight_thread.start()

    # Auto-save every 30 seconds so settings survive a force-kill
    config_manager.start_autosave(app.recoil_menu, app.flashlight_menu, app.settings_menu, interval_seconds=30)

    def on_closing():
        config_manager.save(app.recoil_menu, app.flashlight_menu, app.settings_menu)
        time.sleep(0.1)
        app.destroy()
        os._exit(0)

    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
