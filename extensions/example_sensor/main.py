import gradio as gr
import numpy as np

class ExampleSensor():
    def __init__(self) -> None:
        pass

    def interface(self):
        with gr.Row():
            val = gr.Number(label='sensor value')
            collect_btn = gr.Button(value="read")
        collect_btn.click(self.get_measurement, outputs=[val])

    def get_measurement(self):
        return np.random.randn()
    
    # callback for orchestrator
    def hook(self):
        val = self.get_measurement()
        return val
    
    
    def on_temporal_synchronized_collect_completed(self):
        return self.get_measurement()