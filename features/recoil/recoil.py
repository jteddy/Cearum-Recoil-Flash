from mouse.makcu import makcu_controller
from menu.settings_menu import SettingsMenu
from menu.recoil_menu import RecoilMenu
from menu.games import GAME_BASE_SENSITIVITIES
import time
import random


class recoil:

    @staticmethod
    def jitter(value, max_offset):
        return value + random.uniform(-max_offset, max_offset)

    @staticmethod
    def sens_scalar(app: RecoilMenu, settings: SettingsMenu):
        scalar_mode = settings.get_game_scalar()

        if scalar_mode in GAME_BASE_SENSITIVITIES:
            base = GAME_BASE_SENSITIVITIES[scalar_mode]
            user_sensitivity = settings.get_game_sensitivity()
            return base / user_sensitivity

        # Manual — use the Recoil Scalar slider directly
        return app.get_recoil_scalar()

    @staticmethod
    def run_recoil(app: RecoilMenu, settings: SettingsMenu):
        shot_count = 0
        total_y_movement = 0
        lmb_was_pressed = False
        last_toggle_state = False
        last_cycle_state = False
        # Note: debounce timestamps initialised inside loop setup below

        last_toggle_time = 0.0
        last_cycle_time = 0.0
        DEBOUNCE = 0.3  # seconds — prevents double-trigger without blocking the loop

        while True:
            toggle_key = RecoilMenu.get_toggle_keybind(app)
            if toggle_key != "NONE":
                toggle_key_pressed = makcu_controller.get_button_state(toggle_key)
                now = time.monotonic()
                if toggle_key_pressed and not last_toggle_state and (now - last_toggle_time) >= DEBOUNCE:
                    app.enable_checkbox.toggle()
                    last_toggle_time = now
                last_toggle_state = toggle_key_pressed

            cycle_key = RecoilMenu.get_cycle_bind(app)
            if cycle_key != "NONE":
                cycle_key_pressed = makcu_controller.get_button_state(cycle_key)
                now = time.monotonic()
                if cycle_key_pressed and not last_cycle_state and (now - last_cycle_time) >= DEBOUNCE:
                    RecoilMenu.cycle_script(app)
                    last_cycle_time = now
                last_cycle_state = cycle_key_pressed

            if not RecoilMenu.get_is_enabled(app):
                shot_count = 0
                total_y_movement = 0
                lmb_was_pressed = False
                time.sleep(0.05)
                continue

            recoil_pattern = app.vectors
            lmb_pressed = makcu_controller.get_button_state("LMB")

            if not lmb_pressed and lmb_was_pressed and total_y_movement != 0:
                if RecoilMenu.get_return_crosshair_enabled(app) == True:
                    makcu_controller.move_mouse_smoothly(0, -total_y_movement, 20, RecoilMenu.get_return_speed(app))
                total_y_movement = 0
                shot_count = 0
                lmb_was_pressed = False
                time.sleep(0.02)
                continue

            if not lmb_pressed:
                shot_count = 0
                total_y_movement = 0
                lmb_was_pressed = False
                time.sleep(0.02)
                continue

            if not lmb_was_pressed:
                shot_count = 0
                total_y_movement = 0
                lmb_was_pressed = True

            if recoil_pattern:
                if app.requires_right_button() and not makcu_controller.get_button_state("RMB"):
                    time.sleep(0.02)
                    continue

                if shot_count >= len(recoil_pattern):
                    if app.get_is_recoil_looped():
                        shot_count = 0
                    else:
                        time.sleep(0.02)
                        continue

                x, y, delay = recoil_pattern[shot_count]

                if RecoilMenu.get_is_randomisation_enabled(app) == True:
                    x = recoil.jitter(x, RecoilMenu.get_randomisation_strength(app))
                    y = recoil.jitter(y, RecoilMenu.get_randomisation_strength(app))

                scalar = recoil.sens_scalar(app, settings)

                actual_x = x * RecoilMenu.get_x_control(app) * scalar
                actual_y = y * RecoilMenu.get_y_control(app) * scalar

                start_time = time.perf_counter()
                move_completed = makcu_controller.move_mouse_smoothly(actual_x, actual_y, interrupt_on_lmb_release=True)

                if move_completed:
                    total_y_movement += actual_y

                elapsed = time.perf_counter() - start_time
                remaining_delay = delay - elapsed
                if remaining_delay > 0:
                    time.sleep(remaining_delay)

                shot_count += 1
            else:
                time.sleep(0.02)
