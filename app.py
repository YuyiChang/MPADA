import gradio as gr 
import json
import matplotlib.pyplot as plt
import numpy as np

from webui.mpada_ui import MPADAComponents
# from webui.vna_sweep_ui import SingleSweepComponents
from webui.switch_ui import RP2040Components
from extensions.manager import module_loader, ExtensionManager

ext = ExtensionManager()
mpada = MPADAComponents(extension_manager=ext)

# single_sweep_helper = SingleSweepComponents()

def dummy_print(*config):
    return config

# panels
def config_tab():
    mpada.vna_discovery_interface()
    mpada.vna_init_interface()
    # vna_cal_interface()
    mpada.ant_config_interface()

# 'ysharma/llamas' 'bethecloud/storj_theme'
with gr.Blocks(title="MPADA", theme=gr.themes.Default()) as demo:
    mpada.vna_overview_interface()
    with gr.Tab("Setup"):
        config_tab()
    with gr.Tab("Single Sweep"):
        mpada.single_sweep_tab()
    with gr.Tab("Squential Sweep"):
        mpada.sequential_sweep_tab()
    with gr.Tab("Temporal Sweep"):
        mpada.simple_temporal_sweep_tab()
    with gr.Tab("Extensions"):
        ext.interface()
    # with gr.Tab("Add-ons"):
    #     module_loader()
    

if __name__ == "__main__":
    demo.launch(share=True)
