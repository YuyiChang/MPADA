import gradio as gr

from webui.mpada_server import MPADAServer
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

from webui.configs.config_manager import default_port_mapping, default_gpio_mapping, default_sweep_sequence

def dummy_print(*config):
    print(config)
    return config

def batch_json_load(*str_in):
    out = [json.loads(s) for s in str_in]
    print("=====")
    # print(out[-1].keys())
    for k in out[-1].keys():
        print(k)
    return out


## frontend facing components
class MPADAComponents(MPADAServer):
    def __init__(self, extension_manager=None):
        super().__init__()
        self.extension_manager = extension_manager

    ## frontend interfaces
    def vna_discovery_interface(self):
        gr.Markdown("# Welcome to MPADA!\n ## Connect options")
        
        with gr.Row():
            with gr.Column(min_width=120):
                visa_backend = gr.Dropdown(choices=['@py', 'IVI', 'demo'], value='@py', label='VISA')
            with gr.Column(scale=3):
                device = gr.Dropdown(choices=['None'], value='None', label='VNA address')
                add_direct = gr.Textbox(value="TCPIP0::192.168.0.100::INSTR", label="Direct address")
            with gr.Column(scale=3):
                device_info = gr.Textbox(label='Device name')
                with gr.Row():
                    btn_refresh = gr.Button("refresh")
                    btn_connect = gr.Button("connect")
                    btn_dircon = gr.Button("direct conect")

        btn_refresh.click(fn=self.discover_vna, inputs=[visa_backend], outputs=device)
        btn_connect.click(fn=self.connect_vna, inputs=[device], outputs=[device_info, self.device_name])

        btn_dircon.click(fn=self.connect_vna, inputs=[add_direct], outputs=[device_info, self.device_name])

    # set sweep freq and num of points, and calibrations
    def vna_init_interface(self):
        gr.Markdown("## VNA options")
        with gr.Row():
            with gr.Column():
                # mode = gr.Radio(["demo", "auto"], value="demo", label="vna_mode", info="Choose how to connect to a VNA")
                with gr.Row():
                    f_start = gr.Number(value=0.25, label="freq_start", info="Start frequency (GHz)")
                    f_end = gr.Number(value=8.25, label="freq_stop", info="Stop frequency (GHz)")
                num_pt = gr.Number(value=801, label="num_pt", info="Number of sweep points")
                btn = gr.Button("Set")
            out = gr.Textbox(label="Console")
        btn.click(fn=self.init_vna, inputs=[f_start, f_end, num_pt], outputs=out)

        with gr.Accordion("Calibrations", open=False):
            self.vna_cal_opt()


    def vna_cal_opt(self):
        # gr.Markdown("## Calibration option")
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    mode = gr.Radio(["no_cal", "new_ecal", "use_last_cal"], value="no_cal", label="cal_mode", info="Choose calibration option", scale=2)
                    calset_name = gr.Textbox("MPADA", label="Calset name")
                # cal_opt = gr.Checkbox(label="use_cal", info="Check to enable E-Cal")
                btn = gr.Button("Set")
            out = gr.Textbox(label="Console")
            btn.click(fn=self.apply_cal, inputs=[mode, calset_name], outputs=out)


    def vna_overview_interface(self):
        with gr.Row():
            self.device_name = gr.Textbox(value='None', label="Device name", max_lines=1, scale=8)
            btn_reset = gr.Button("vna soft reset")
            btn_autoscale = gr.Button("autoscale")

            btn_reset.click(self.on_vna_reset_button_pressed)
            btn_autoscale.click(self.on_vna_autoscale_button_pressed)

    # antenna and sweep config
    def ant_config_interface(self):
        gr.Markdown("## Antenna and sweep options")
        with gr.Row():
            with gr.Column():
                switch_mode = gr.Radio(["no_switch", "ftdi", "rp2040", "keysight"], 
                                    value="rp2040", 
                                    label="switch_mode", 
                                    info="Choose RF switch option")
                
                # df_port_mapping = gr.DataFrame()
                
                # btn = gr.Button("Set")
            out = gr.Textbox(label="Console")
            # btn.click(fn=dummy_print, inputs=[switch_mode], outputs=out)

        # with gr.Row():
        #     rf_map = gr.Code(default_port_mapping, language='json', label="RF ports")
        #     rf_map_json = gr.JSON()
        #     # port_mapping = gr.Code(default_port_mapping, language='json', label="Port mappings")
        with gr.Row():
            with gr.Column():
                gpio_map = gr.Code(default_gpio_mapping, language='json', label="GPIOs")
                apply_btn = gr.Button("apply")
            gpio_map_json = gr.JSON()

        tx_port = gr.Radio(label='TX ports')
        rx_port = gr.Radio(label='RX ports')

        tx_port.change(fn=self.update_rf_port, inputs=[tx_port, rx_port])
        rx_port.change(fn=self.update_rf_port, inputs=[tx_port, rx_port])

        apply_btn.click(fn=self.config_ant_switch, inputs=[switch_mode, gpio_map], outputs=[gpio_map_json, tx_port, rx_port])
        

    ## sweep
    def single_sweep_tab(self):
        gr.Markdown("# Single sweep")

        with gr.Row():
            num = gr.Number(value=1, label="Number of trigger", scale=2)
            btn = gr.Button("Start")
            # out = gr.Textbox(scale=5)

        with gr.Row():
            out_plot = gr.LinePlot(scale=5)
            out_file = gr.File()

        with gr.Accordion("Tabular data", open=False):  
            out_df = gr.DataFrame()
        btn.click(fn=self.get_sweep_data, inputs=num, outputs=[out_plot, out_df, out_file])

    ## sequencial sweep
    def sequential_sweep_tab(self):
        gr.Markdown('# Sequential sweep')

        with gr.Row():
            with gr.Column():
                gpio_map = gr.Code(default_sweep_sequence, language='json', label="Sweep sequence")
                apply_btn = gr.Button("apply")
            sweep_data = gr.JSON()
            apply_btn.click(fn=self.apply_sequencial_sweep_setting, 
                                inputs=gpio_map, outputs=sweep_data)

       
        with gr.Row():
            with gr.Row():
                with gr.Column(scale=5):
                    with gr.Row():
                        mcu_delay = gr.Number(value=0.2, label="MCU pin holding time (sec)")
                        df_name = gr.Textbox(value="dataframe", label="CSV name")
                        num_cycle = gr.Number(value=1, label="Number of scan cycles")

                        enable_orchestrator = gr.Checkbox(value=True, label="Enable Orchestrator")
                        num_repeat = gr.Number(value=1, label="Number of repetition")
                    notepad = gr.Text(label="Note")


                btn = gr.Button("Start")
                btn_stop = gr.Button("Stop")


        ### result visualizations
        with gr.Row():
            # out_plot = gr.LinePlot(scale=5)
            out_plot = gr.Plot(scale=3)
            out_file = gr.File()

        with gr.Accordion("Tabular data", open=False):  
            out_df = gr.DataFrame()

        # extension opts
        chk_grp = self.extention_modules(enable_temporal_cb=False)  

        sweep_evt = btn.click(fn=self.get_sequential_sweep_data, 
                            inputs=[mcu_delay, df_name, num_cycle, enable_orchestrator, num_repeat, notepad], 
                            outputs=[out_plot, out_df, out_file])
        btn_stop.click(cancels=sweep_evt)

    ## single channel temporal sweep
    def simple_temporal_sweep_tab(self):
        gr.Markdown("# Temporal sweep - single channel")

        with gr.Row():
            sweep_time = gr.Number(value=10, label="Sweep time (sec)")
            sweep_interval = gr.Number(value=0.1, label="Sweep interval (sec)")
            num_sweep = gr.Number(value=int(10/0.1), label="Number of sweep")
            button = gr.Button(value="Start")

        with gr.Row():
            with gr.Tab("spectrogram"):
                fig_spectrogram = gr.Plot()
            with gr.Tab("timestamp"):
                fig_timestamp = gr.Plot(scale=1)
            
            with gr.Column():
                tab_list, df_list = [], []
                # with gr.Blocks():
                for i in range(5):
                    visible = True if i == 0 else False
                    curr_tab = gr.Tab(label=f'data viewer {i}', visible=visible)
                    tab_list.append(curr_tab)
                    with curr_tab:
                        curr_df = gr.DataFrame(visible=visible)
                        df_list.append(curr_df)
                out_file = gr.File()

        # extension opts
        chk_grp = self.extention_modules()


        sweep_time.change(self.update_temporal_sweep_config, 
                          inputs=[sweep_time, sweep_interval],
                          outputs=num_sweep)
        sweep_interval.change(self.update_temporal_sweep_config, 
                          inputs=[sweep_time, sweep_interval],
                          outputs=num_sweep)
        button.click(self.start_temporal_sweep, 
                     inputs=[num_sweep, sweep_interval, chk_grp],
                     outputs=[fig_timestamp, fig_spectrogram, out_file, *df_list, *tab_list]
                     )


    def extention_modules(self, enable_temporal_cb=True):
        if self.extension_manager is not None:
            chk_grp = gr.CheckboxGroup(choices=self.extension_manager.loaded_module.keys(),
                                        label="Extension callbacks enable", visible=enable_temporal_cb)
            with gr.Accordion("Extensions", open=False):
                self.extension_manager.interface()
        else:
            chk_grp = gr.CheckboxGroup(label="Extension callbacks enable")
        return chk_grp