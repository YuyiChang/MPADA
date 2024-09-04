import os
os.environ["BLINKA_U2IF"] = "1"
import gradio as gr
import board
import digitalio
import time


class GenericStepper():
    def __init__(self):
        self.init_stepper()

    def interface(self):
        init_stepper_btn = gr.Button(value='init stepper')

        init_stepper_btn.click(fn=self.init_stepper)

        num_pulse = gr.Number(value=10, label='Num of pulse')

        fwd = gr.Checkbox(label='FWD')
        run = gr.Button(value="run")
        run.click(self.run_stepper, inputs=[num_pulse, fwd])

        ena = gr.Checkbox(label="Disable", value=True)
        ena.change(self.change_ena, inputs=[ena])

    def change_ena(self, ena):
        self.ENA.value = ena

    def init_stepper(self):
        self.PUL = digitalio.DigitalInOut(board.GP16)
        self.PUL.direction = digitalio.Direction.OUTPUT
        self.PUL.value = True

        self.DIR = digitalio.DigitalInOut(board.GP17)
        self.DIR.direction = digitalio.Direction.OUTPUT
        self.DIR.value = False

        self.ENA = digitalio.DigitalInOut(board.GP18)
        self.ENA.direction = digitalio.Direction.OUTPUT
        self.ENA.value = True

        self.buffer_ena = digitalio.DigitalInOut(board.GP19)
        self.buffer_ena.direction = digitalio.Direction.OUTPUT
        self.buffer_ena.value = True 

    def hook(self, n_steps=5):
        self.buffer_ena.value = False
        self.ENA.value = False
        time.sleep(0.1)
        self.run_stepper(num_pulse=n_steps)

        self.buffer_ena.value = True
        # time.sleep(0.1)
        time.sleep(2)
        # self.ENA.value = True
        return "stepper ok"

    def hook_cleanup(self):
        print("stepper disable")
        self.ENA.value = True

    def run_stepper(self, num_pulse=5, fwd=True, time_delay=25e-3):
        self.DIR.value = fwd
        self.PUL.value = False
        time.sleep(10e-3)
        self.PUL.value = True
        print("step complete")

    # def run_stepper(self, num_pulse=5, fwd=True, time_delay=25e-3):
    #     num_pulse = int(num_pulse)
    #     self.DIR.value = fwd

    #     # self.ENA.value = True
    #     for _ in range(num_pulse):
    #         self.PUL.value = True
    #         time.sleep(time_delay)
    #         self.PUL.value = False
    #         time.sleep(time_delay)

    #     time.sleep(0.5)
    #     print("stepping complete")

    def cycle(self, num_pulse=5):
        self.run_stepper(num_pulse=num_pulse, fwd=True)
        self.run_stepper(num_pulse=num_pulse, fwd=False)


if __name__ == '__main__':
    stepper = GenericStepper()

    with gr.Blocks() as demo:
        stepper.interface()

    demo.launch(share=True)
    