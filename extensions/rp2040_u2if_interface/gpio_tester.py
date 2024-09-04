import gradio as gr
import sys

import os
cwd = os.getcwd()
print(cwd)
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from mpada.usb_interfaces.rp2040 import RP2040
from mpada.usb_interfaces.default import DefaultMCU

class RP2040Components():
    def __init__(self) -> None:
        self.mcu = DefaultMCU()
        # pass

    def interface(self):
        # with gr.Row():
        init_btn = gr.Button("connect to RP2040")
        with gr.Row():
            pin_checkboxgrp = gr.CheckboxGroup(label="GPIO", scale=9)
            console = gr.Textbox(scale=1, label="Console")
        # with gr.Row():
        #     all_on = gr.Button("All on")
        #     all_off = gr.Button("All off")
        # https://learn.adafruit.com/assets/102148
        pin_out = '<img style="display: block;-webkit-user-select: none;margin: auto;background-color: hsl(0, 0%, 90%);transition: background-color 300ms;" src="https://cdn-learn.adafruit.com/assets/assets/000/102/148/medium800/sensors_pico_u2if_pinout.png">'
        gr.HTML(pin_out)
        

        init_btn.click(self.init_device, inputs=None, outputs=[console, pin_checkboxgrp])
        pin_checkboxgrp.change(self.update_pin, inputs=pin_checkboxgrp, outputs=console)

    def init_device(self):
        try:
            self.mcu = RP2040()
            self.mcu.init_board()

            for pin in self.mcu.gpio_list:
                self.mcu.init_pin(pin)

            return 'RP2040 init OK', gr.CheckboxGroup(choices=self.mcu.gpio_list)
        except Exception as e:
            print(str(e))
            return str(e), gr.CheckboxGroup()
        
    def update_pin(self, pin_group):
        print(pin_group)
        try: 
            self.reset_pin()
            self.set_pin(pin_group)
            return pin_group
        except Exception as e:
            print(str(e))
            return str(e)

    def reset_pin(self):
        for pin in self.mcu.gpio_list:
            self.mcu.set_pin(pin, False)

    def set_pin(self, pin_group):
        for pin in pin_group:
            self.mcu.set_pin(pin, True)
    
if __name__ == '__main__':
    switch = RP2040Components()
    with gr.Blocks() as demo:
        switch.interface()
    demo.launch()