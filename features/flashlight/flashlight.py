import time
import threading
from mouse.makcu import makcu_controller
from menu.flashlight_menu import FlashlightMenu


class flashlight:
    @staticmethod
    def _delayed_click(keybind: str, delay: float):
        """Wait for the pre-fire delay then send the flashlight click."""
        time.sleep(delay)
        makcu_controller.click_button(keybind)

    @staticmethod
    def run_flashlight(app: FlashlightMenu):
        """
        Behaviour:
        - Watches for LMB press.
        - Only triggers flashlight if LMB is held for longer than the hold
          threshold — this prevents regular UI clicks from firing the flashlight.
        - Cooldown prevents re-triggering on rapid follow-up shots.
        - Click is dispatched on a fire-and-forget thread so it never blocks.
        """
        lmb_was_pressed = False
        lmb_press_time = 0.0
        cooldown_until = 0.0
        threshold_triggered = False

        while True:
            if not app.get_is_enabled():
                lmb_was_pressed = False
                threshold_triggered = False
                time.sleep(0.02)
                continue

            keybind = app.get_flashlight_keybind()
            if keybind == "NONE":
                lmb_was_pressed = False
                threshold_triggered = False
                time.sleep(0.02)
                continue

            lmb_pressed = makcu_controller.get_button_state("LMB")
            now = time.monotonic()

            # Rising edge — record when LMB went down
            if lmb_pressed and not lmb_was_pressed:
                lmb_press_time = now
                threshold_triggered = False

            # While held — check if hold threshold has been exceeded
            if lmb_pressed and not threshold_triggered:
                held_duration = now - lmb_press_time
                if held_duration >= app.get_hold_threshold():
                    threshold_triggered = True
                    if now >= cooldown_until:
                        cooldown_until = now + app.get_cooldown_ms()
                        threading.Thread(
                            target=flashlight._delayed_click,
                            args=(keybind, app.get_pre_fire_delay()),
                            daemon=True,
                        ).start()

            # Falling edge — reset
            if not lmb_pressed and lmb_was_pressed:
                threshold_triggered = False

            lmb_was_pressed = lmb_pressed
            time.sleep(0.005)  # 5ms polling
