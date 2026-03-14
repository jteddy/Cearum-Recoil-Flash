import time
import threading
from mouse.makcu import makcu_controller
from menu.flashlight_menu import FlashlightMenu

class flashlight:
    @staticmethod
    def _delayed_click(keybind: str, delay: float):
        """Wait for the LMB event to clear the makcu, then send the flashlight click."""
        time.sleep(delay)
        makcu_controller.click_button(keybind)

    @staticmethod
    def run_flashlight(app: FlashlightMenu):
        """
        Runs in its own daemon thread.

        Behaviour:
        - Watches for LMB rising edge (not pressed → pressed).
        - On the FIRST shot of a burst, schedules the flashlight keybind click
          after a short pre-fire delay so the LMB event is not disrupted.
        - While the cooldown is still active subsequent LMB presses are ignored,
          so the flashlight is not toggled off mid-burst or on rapid follow-up shots.
        - The flashlight click is dispatched on a fire-and-forget thread so it
          never blocks the main polling loop.
        """
        lmb_was_pressed = False
        cooldown_until = 0.0  # monotonic timestamp

        while True:
            if not app.get_is_enabled():
                lmb_was_pressed = False
                time.sleep(0.02)
                continue

            keybind = app.get_flashlight_keybind()
            if keybind == "NONE":
                lmb_was_pressed = False
                time.sleep(0.02)
                continue

            lmb_pressed = makcu_controller.get_button_state("LMB")

            # Detect rising edge — new press only
            if lmb_pressed and not lmb_was_pressed:
                now = time.monotonic()
                if now >= cooldown_until:
                    # Set cooldown from this first shot
                    cooldown_until = now + app.get_cooldown_ms()

                    # Dispatch a delayed click so it doesn't collide with LMB
                    threading.Thread(
                        target=flashlight._delayed_click,
                        args=(keybind, app.get_pre_fire_delay()),
                        daemon=True,
                    ).start()

            lmb_was_pressed = lmb_pressed
            time.sleep(0.005)  # 5 ms polling — tight enough to catch every press
