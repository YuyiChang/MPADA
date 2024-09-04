import os
os.environ["BLINKA_U2IF"] = "1"
import time
import gradio as gr

# resource manager for RP2040
# running UF2 firmware: https://learn.adafruit.com/circuitpython-libraries-on-any-computer-with-raspberry-pi-pico/other-rp2040-boards
class RP2040():
    def __init__(self) -> None:
        self.gpio_state = {}
        self.last_on = set()
        self.board = None

    def interface(self):
        mcu_enable = gr.Checkbox()
        mcu_enable.change(self.manage_resource, inputs=mcu_enable)

    def manage_resource(self, state):
        print(state)
        if state:
            self.init_board()
        else:
            self.__init__()

    def init_board(self):
        import digitalio
        import board
        self.board = board
        self.digitalio = digitalio
        
        # get all GPIO pins
        self.gpio_list = []
        for pin in dir(board):
            self.gpio_list.append(pin) if 'GP' in pin else None
        self.gpio_list = sorted(self.gpio_list, key=len)

        print("available GPIOs: ", self.gpio_list)
        
    def init_pin(self, pin_id, mode='OUTPUT'):
        assert pin_id in self.gpio_list, print(f"{pin_id} not in gpio_list")
        pin = self.digitalio.DigitalInOut(getattr(self.board, pin_id)) 
        pin.direction = self.digitalio.Direction.OUTPUT
        setattr(self, pin_id, pin)   

        self.gpio_state[pin_id] = False

    def set_pin(self, pin_id, mode:bool):
        assert pin_id in self.gpio_list
        pin = getattr(self, pin_id)
        pin.value = mode
        
    def update_pin_state_on(self, pin_list: list):
        pin_list = set(pin_list)

        pin_to_set_false = self.last_on - pin_list
        
        for p in pin_to_set_false:
            self.set_pin(p, False)
        print(pin_to_set_false, pin_list)

        self.last_on = pin_list

        for p in pin_list:
            self.set_pin(p, True)
