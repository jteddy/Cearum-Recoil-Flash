import time
import threading
from makcu import create_controller, MouseButton


class makcu_controller:
    controller = None

    button_states = {
        "LMB": False,
        "RMB": False,
        "MMB": False,
        "M4": False,
        "M5": False
    }

    connection_lock = threading.Lock()
    command_lock = threading.Lock()  # Prevents simultaneous writes to the device
    is_connected_flag = False
    _on_disconnected = None  # Callback fired when device disconnects 


    @staticmethod
    def is_connected():
        with makcu_controller.connection_lock:
            return (
                makcu_controller.is_connected_flag
                and makcu_controller.controller is not None
            )


    @staticmethod
    def connect():
        with makcu_controller.connection_lock:
            if makcu_controller.controller is None:
                try:
                    makcu_controller.controller = create_controller(
                        debug=False,
                        auto_reconnect=True
                    )

                    def on_button_event(button: MouseButton, pressed: bool):
                        if button == MouseButton.LEFT:
                            makcu_controller.button_states["LMB"] = pressed
                        elif button == MouseButton.RIGHT:
                            makcu_controller.button_states["RMB"] = pressed
                        elif button == MouseButton.MIDDLE:
                            makcu_controller.button_states["MMB"] = pressed
                        elif button == MouseButton.MOUSE4:
                            makcu_controller.button_states["M4"] = pressed
                        elif button == MouseButton.MOUSE5:
                            makcu_controller.button_states["M5"] = pressed

                    makcu_controller.controller.set_button_callback(on_button_event)
                    makcu_controller.controller.enable_button_monitoring(True)

                    makcu_controller.is_connected_flag = True

                except Exception as e:
                    print(f"[MAKCU] Connection error: {e}")
                    makcu_controller.is_connected_flag = False
                    makcu_controller.controller = None
                    return None

            return makcu_controller.controller

    @staticmethod
    def StartButtonListener():
        makcu_controller.connect()

    @staticmethod
    def register_disconnect_callback(callback) -> None:
        """Register a function to call when the device disconnects unexpectedly."""
        makcu_controller._on_disconnected = callback

    @staticmethod
    def _notify_disconnected() -> None:
        """Fire the disconnect callback if one is registered."""
        if makcu_controller._on_disconnected:
            try:
                makcu_controller._on_disconnected()
            except Exception:
                pass

    @staticmethod
    def click_button(button_name: str):
        if not makcu_controller.is_connected():
            return False

        mck = makcu_controller.controller
        try:
            with makcu_controller.command_lock:
                if button_name == "LMB":
                    mck.click(MouseButton.LEFT)
                elif button_name == "RMB":
                    mck.click(MouseButton.RIGHT)
                elif button_name == "MMB":
                    mck.click(MouseButton.MIDDLE)
                elif button_name == "M4":
                    mck.click(MouseButton.MOUSE4)
                elif button_name == "M5":
                    mck.click(MouseButton.MOUSE5)
            return True
        except Exception as e:
            print(f"[MAKCU] Click error: {e}")
            makcu_controller.is_connected_flag = False
            makcu_controller._notify_disconnected()
            return False


    @staticmethod
    def simple_move_mouse(x, y):
        if not makcu_controller.is_connected():
            return False

        try:
            with makcu_controller.command_lock:
                makcu_controller.controller.move(x, y)
            return True
        except Exception as e:
            print(f"[MAKCU] Move error: {e}")
            makcu_controller.is_connected_flag = False
            makcu_controller._notify_disconnected()
            return False


    @staticmethod
    def move_mouse_smoothly(dx, dy, steps=20, duration=0.05):
        if not makcu_controller.is_connected():
            return False

        if dx == 0 and dy == 0:
            return False

        def ease_out_quad(t):
            return t * (2 - t)

        mck = makcu_controller.controller
        step_delay = duration / steps

        try:
            accumulated_x = 0.0
            accumulated_y = 0.0

            for i in range(steps):
                t = (i + 1) / steps
                eased = ease_out_quad(t)

                target_x = dx * eased
                target_y = dy * eased

                delta_x = target_x - accumulated_x
                delta_y = target_y - accumulated_y

                move_x = round(delta_x)
                move_y = round(delta_y)

                accumulated_x += move_x
                accumulated_y += move_y

                if move_x or move_y:
                    with makcu_controller.command_lock:
                        mck.move(move_x, move_y)

                time.sleep(step_delay)

            return True

        except Exception as e:
            print(f"[MAKCU] Smooth move error: {e}")
            makcu_controller.is_connected_flag = False
            makcu_controller._notify_disconnected()
            return False


    @staticmethod
    def get_button_state(button_name: str):
        return makcu_controller.button_states.get(button_name, False)


    @staticmethod
    def disconnect():
        with makcu_controller.connection_lock:
            if makcu_controller.controller:
                try:
                    makcu_controller.controller.disconnect()
                except Exception:
                    pass

                makcu_controller.controller = None
                makcu_controller.is_connected_flag = False
