import json
import os
import sys
import shutil
import threading
import time


def _config_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        base = os.path.dirname(base)  # go up from menu/ to project root
    return os.path.join(base, "config.json")


def save(recoil_menu, flashlight_menu, settings_menu) -> None:
    """
    Atomic save — writes to a temp file first, then replaces the real config
    only on success. This means a crash mid-save can never corrupt config.json.
    """
    path = _config_path()
    tmp_path = path + ".tmp"

    data = {
        "recoil":     recoil_menu.get_config(),
        "flashlight": flashlight_menu.get_config(),
        "settings":   settings_menu.get_config(),
    }

    try:
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        shutil.move(tmp_path, path)  # atomic replace
    except Exception as e:
        print(f"[Config] Save error: {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def load(recoil_menu, flashlight_menu, settings_menu) -> None:
    """
    Load config, with corruption protection — if the file is invalid JSON,
    attempt to recover from a backup, otherwise fall back to defaults silently.
    """
    path = _config_path()
    backup_path = path + ".bak"

    if not os.path.exists(path):
        return  # first launch — use widget defaults

    # Try loading the main config
    data = _try_load(path)

    # If corrupt, try the backup
    if data is None and os.path.exists(backup_path):
        print("[Config] Main config corrupt, attempting backup restore...")
        data = _try_load(backup_path)

    if data is None:
        print("[Config] Could not load config, using defaults.")
        return

    # Write a fresh backup from the successfully loaded data
    try:
        shutil.copy2(path, backup_path)
    except Exception:
        pass

    recoil_menu.load_config(data.get("recoil", {}))
    flashlight_menu.load_config(data.get("flashlight", {}))
    settings_menu.load_config(data.get("settings", {}))


def _try_load(path: str) -> dict | None:
    """Attempt to parse a JSON file. Returns None if invalid or unreadable."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Config] Failed to load {path}: {e}")
        return None


def start_autosave(recoil_menu, flashlight_menu, settings_menu, interval_seconds: int = 30) -> None:
    """
    Starts a background daemon thread that saves config every `interval_seconds`.
    Protects against settings loss if the program is force-killed.
    """
    def _autosave_loop():
        while True:
            time.sleep(interval_seconds)
            save(recoil_menu, flashlight_menu, settings_menu)

    thread = threading.Thread(target=_autosave_loop, daemon=True)
    thread.start()
