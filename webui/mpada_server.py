import gradio as gr
from mpada.vna_comm import VnaVisa
from mpada.vna_sweep import VnaSweepConfig
from mpada.vna_simulator import DemoVisa
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from mpada.usb_interfaces.default import DefaultMCU
import time
from tqdm import tqdm
import threading
import tempfile
import itertools
tempfile._get_candidate_names = lambda: itertools.repeat('mpada') 
from zipfile import ZipFile
import os

# callback func
class MPADAServer():
    def __init__(self) -> None:
        self.visa = DemoVisa()
        self.port_tx = []
        self.port_rx = []

        self.gpio_dict = {}

        self.mcu = DefaultMCU()

    ## interface callbacks
    def discover_vna(self, visa_backend):
        if visa_backend == '@py':
            self.visa = VnaVisa(backend=visa_backend)
        elif visa_backend == 'demo':
            self.visa = DemoVisa()
        else:
            self.visa = VnaVisa()
        resource_list = self.visa.get_all_resource()

        choices = [res for res in resource_list]
        print(choices)

        return gr.Dropdown(choices=choices)
    
    def connect_vna(self, device):
        print("connecting to device: ", device)

        rtn = self.visa.connect_instrument(device)
        print(rtn)

        return rtn, rtn

    def init_vna(self, f_start, f_stop, num_pt, *config):
        self.vna_config = VnaSweepConfig()
        self.vna_config.set_freq(f_start=f_start*1e9, 
                                 f_stop=f_stop*1e9, 
                                 num_pt=num_pt)
        self.visa.init_ins(self.vna_config)
        return self.visa.get_freq()

    def get_sweep_data(self, num):
        self.visa.ins.write("SENS:SWE:MODE SING;*WAI")
        self.visa.ins.write("CALC:DATA? SDATA")
        data = self.visa.ins.read()
        data = self.process_trace(data)
        print(data)
        print(len(data))

        df = pd.DataFrame({'freq': np.linspace(0.5, 6, len(data)), 
                           'data': data})
        df.to_csv("dataframe.csv", index=None)

        return gr.LinePlot(df, x='freq', y='data', width=900, height=700), df, "dataframe.csv"

    def process_trace(self, trace):
        data = np.fromstring(trace, sep=',')
        data = data[::2] + 1j*data[1::2]
        return np.abs(data)
    
    def config_ant_switch(self, switch_mode, gpio_map):
        tx_port_cbg = gr.Radio()
        rx_port_cbg = gr.Radio()

        self.port_tx = []
        self.port_rx = []

        if switch_mode == 'no_switch':
            gpio_dict = {"TX1": [], "RX1": []}            
            
        elif switch_mode == 'rp2040':
            from mpada.usb_interfaces.rp2040 import RP2040
            self.mcu = RP2040()
            self.mcu.init_board()
            gpio_dict = json.loads(gpio_map)

            gpio_in_use = self._get_all_gpio(gpio_dict)
            for g in gpio_in_use: self.mcu.init_pin(g)

            # gpio_list = self._get_all_gpio(gpio_dict)

            for port in gpio_dict.keys():
                if 'TX' in port:
                    self.port_tx.append(port)
                elif 'RX' in port:
                    self.port_rx.append(port)

            tx_port_cbg = gr.Radio(choices=self.port_tx, value=self.port_tx[0])
            rx_port_cbg = gr.Radio(choices=self.port_rx, value=self.port_rx[0])
        
        else:
            raise NotImplemented()

        self.gpio_dict = gpio_dict
        return gpio_dict, tx_port_cbg, rx_port_cbg
    
    def _get_all_gpio(self, gpio_dict):
        gpio = []
        for v in gpio_dict.values():
            gpio.extend(v)
        return gpio
    
    def _get_gpio_group(self, rf_port):
        gpio = []
        for p in rf_port:
            if p in self.gpio_dict.keys():
                gpio.extend(self.gpio_dict[p])
        print("unique gpios: ", gpio)
        return gpio

    def update_rf_port(self, tx_port, rx_port):
        rf_port = [tx_port, rx_port]
        # print("233", [tx_port], [rx_port])
        gpio_on = self._get_gpio_group(rf_port)

        # print("RF ports selected: ", rf_port, 
        #       "\nGPIOs True on ", gpio_on)
        # print("========= ", gpio_on)
        self.mcu.update_pin_state_on(gpio_on)

    def apply_sequencial_sweep_setting(self, sequence):
        print(sequence)

        self.seq_dict = json.loads(sequence)
        # df = pd.DataFrame.from_dict(sequence)
        # print(df)
        for k, v in self.seq_dict.items():
            print(k, v)

        return json.loads(sequence)
    
    def single_sweep(self):
        trace = self.visa.sweep_and_get_trace()
        return trace
    
    def _sequential_sweep(self, df, num_cycle, mcu_delay):
        header_to_plot = []
        out = {}
        for cycle in range(num_cycle):
            for k, v in self.seq_dict.items():
                print(f"sweep step {k}, {v}")

                # set mcu GPIOs
                self.update_rf_port(v[0], v[1])
                time.sleep(mcu_delay)

                # trigger and get trace
                trace = self.single_sweep()

                cycle_id = str(cycle).zfill(2)
                
                # save trace
                df[f'{k}_mag_{cycle_id}'] = np.abs(trace)
                # df[f'{k}_real_{cycle_id}'] = np.real(trace)
                # df[f'{k}_imag_{cycle_id}'] = np.imag(trace)
                out[f'{k}_{cycle_id}'] = trace
                header_to_plot.append(f'{k}_mag_{cycle_id}')

                time.sleep(0.1)
        return df, header_to_plot, out

    def get_sequential_sweep_data(self, mcu_delay=0.2, df_name='dataframe', num_cycle=1, 
                                  enable_orch=False, auto_repeat=1, note=None):
        print(self.seq_dict)

        df = pd.DataFrame({'frequency (GHz)': np.linspace(self.vna_config.freq_start / 1e9, 
                                                          self.vna_config.freq_stop / 1e9, 
                                                          self.vna_config.num_pt)})

        out = {'freq': np.linspace(self.vna_config.freq_start / 1e9, 
                                   self.vna_config.freq_stop / 1e9, 
                                   self.vna_config.num_pt)}
        
        out['meta'] = {
            'note': note,
            'mcu_delay': mcu_delay,
            'num_cycle': num_cycle,
            'auto_repeat': auto_repeat
        }
        
        enable_auto = True if auto_repeat > 1 else False
        print(enable_auto, auto_repeat, enable_orch)
        if enable_auto:
            for i in tqdm(range(auto_repeat)):
                df_curr = pd.DataFrame({'frequency (GHz)': np.linspace(self.vna_config.freq_start / 1e9, 
                                                          self.vna_config.freq_stop / 1e9, 
                                                          self.vna_config.num_pt)})
                
                df_curr, header_to_plot, trace_out = self._sequential_sweep(df_curr, num_cycle, mcu_delay)

                out[f'trace_{i}'] = trace_out

                csv_name = f"{df_name}_{str(i).zfill(2)}.csv"
                # df_curr.to_csv(csv_name, index=None)

                if enable_orch:
                    res = self.extension_manager.loaded_module['orchestrator']()
                    out[f'ext_{i}'] = res
            df = df_curr

        else:
            df, header_to_plot, trace_out = self._sequential_sweep(df, num_cycle, mcu_delay)   
            out['trace'] = trace_out
            if enable_orch:
                print("running orchestrator")
                res = self.extension_manager.loaded_module['orchestrator']()   
                out['ext'] = res

        # orchestrator clean up
        self.extension_manager.loaded_module['orchestrator'].clean_up()

        npy_name = self._to_npy(out)

        # end of sweep, reset
        self.update_rf_port(None, None)

        csv_name = f"{df_name}.csv"
        df.to_csv(csv_name, index=None)

        fig = self._plot_df(df, header_to_plot=header_to_plot)

        # return gr.LinePlot(df, x='frequency (GHz)', y='magnitude', width=900, height=700), df, "dataframe.csv"
        return fig, df, [csv_name, npy_name]

    
    def _plot_df(self, df, x_name='frequency (GHz)', header_to_plot='mag'):
        fig = plt.figure()
        for h in header_to_plot:
            plt.plot(df[x_name], df[h], label=h)

        plt.xlabel('frequency (GHz)')
        plt.ylabel('magnitude')
        plt.legend()
        return fig
    
    def apply_cal(self, cal_mode, calset_name):
        print(f"selected calmode: {cal_mode} and calset name: {calset_name}")
        if cal_mode == "new_ecal":
            self.visa.calibration(name=calset_name)
        return cal_mode
    
    def on_vna_reset_button_pressed(self):
        self.visa.soft_reset(self.vna_config)

    def on_vna_autoscale_button_pressed(self):
        self.visa.auto_rescale()

    def update_temporal_sweep_config(self, sweep_time, sweep_interval):
        return int(sweep_time / sweep_interval)
    
    def spawn_temporal_extension_calls(self, extension_enable, iterations_event, sweep_time):
        for m in extension_enable:
            assert m in self.extension_manager.loaded_module.keys()
            ext_module = self.extension_manager.loaded_module[m]
            print(ext_module)
            try:
                ext_module.on_temporal_synchronized_collect(stop_flag=iterations_event,
                                                            daq_duration=sweep_time)
            except Exception as e:
                Warning(str(e))

    def collect_temporal_extension_calls(self, extension_enable):
        data_out = {}
        for m in extension_enable:
            assert m in self.extension_manager.loaded_module.keys()
            ext_module = self.extension_manager.loaded_module[m]
            try:
                data = ext_module.on_temporal_synchronized_collect_completed()
                # data.to_csv('ext_out.csv', index=False)
                data_out[m] = data
            except Exception as e:
                Warning(str(e))
        return data_out

    def start_temporal_sweep(self, 
                             num_sweep, 
                             sweep_interval, 
                             extension_enable):

        print("Using extensions:", extension_enable)
        print("num of sweep: ", num_sweep)
        print("sweep interval: ", sweep_interval)
        sweep_time = num_sweep * sweep_interval

        _ = self.visa.sweep_and_get_trace()

        results = [None] * num_sweep
        timestamps = np.zeros((num_sweep,), dtype=int)

        iterations_event = threading.Event()
        task_thread = threading.Thread(target=self._temporal_helper, 
                                       args=(sweep_interval, 
                                             results, 
                                             iterations_event, 
                                             num_sweep,
                                             timestamps))
        task_thread.daemon = True

        # start any enabled extension calls here
        self.spawn_temporal_extension_calls(extension_enable,
                                            iterations_event,
                                            sweep_time)

        # start VNA sweep
        task_thread.start()
        iterations_event.wait()
        iterations_event.set()

        # extension callbacks post completion steps
        data_out = self.collect_temporal_extension_calls(extension_enable)

        # trace post completion
        df_trace = pd.DataFrame(data={'timestamp':timestamps,
                                      'data':results})   
        data_out['trace'] = df_trace

        # csv to temp files
        file_list = self._dict_to_csv_collection(data_out)      

        # csv to blocks
        df_list, tab_list = self._dict_to_csv_blocks(data_out)

        # timestamp plot
        fig = self._create_sample_interval_hist(timestamps, sweep_interval)

        # spectrogram plot
        fig_spec = self._create_spectrogram(results, sweep_interval)

        return fig, fig_spec, file_list, *df_list, *tab_list
    
    def _create_spectrogram(self, results, sweep_interval):
        # print(results[0])
        mat = np.abs(np.column_stack(results))
        fig = plt.figure()
        plt.imshow(mat, aspect='auto', origin='lower', cmap='plasma', 
                   extent=[0, sweep_interval* mat.shape[1], 0, mat.shape[0]])
        plt.ylabel('freq index')
        plt.xlabel('time (s)')
        return fig
    
    def _dict_to_csv_blocks(self, data_out):
        df_list = [gr.DataFrame(value=v, visible=True) for v in data_out.values()]
        tab_list = [gr.Tab(label=v, visible=True) for v in data_out.keys()]

        tab_list = tab_list + [gr.Tab(visible=False) for _ in range(5-len(tab_list))]
        df_list = df_list + [gr.DataFrame(visible=False) for _ in range(5-len(df_list))]
        return df_list, tab_list
    
    def _to_npy(self, data):
        common_timestamp = time.perf_counter_ns()
        f_npy = tempfile.NamedTemporaryFile(suffix='.npy', 
                                            delete=False, 
                                            prefix=f'{common_timestamp}-')
        with open(f_npy.name, 'wb') as f:
            np.save(f, data, allow_pickle=True)
        return f_npy.name
    
    def _dict_to_csv_collection(self, data):
        common_timestamp = time.perf_counter_ns()
        file_list = []
        for k, v in data.items():
            trace_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False,
                                                     prefix=f'{common_timestamp}-{k}-')
            v.to_csv(trace_file.name, index=False)
            file_list.append(trace_file.name)

        # dump dict to pickled numpy file
        f_npy = tempfile.NamedTemporaryFile(suffix='.npy', 
                                            delete=False, 
                                            prefix=f'{common_timestamp}-{k}-')
        with open(f_npy.name, 'wb') as f:
            np.save(f, data, allow_pickle=True)
            file_list.append(f_npy.name)
        print(file_list)

        zip_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False,
                                               prefix=f'{common_timestamp}-')
        with ZipFile(zip_file.name, 'w') as z:
            for f in file_list:
                z.write(f, os.path.basename(f))
        file_list.append(zip_file.name)
        return file_list
    
    def _create_sample_interval_hist(self, timestamps, sweep_interval):
        timeinterval = np.diff(timestamps)
        fig = plt.figure()
        # plt.plot(timeinterval)
        plt.hist(timeinterval * 1e-9 * 1e3)
        plt.axvline(x=sweep_interval*1e3, color='r')
        plt.xlabel('time (ms)')     
        return fig

    def _temporal_helper(self, sweep_interval, results, iterations_event, num_sweep, timestamps):
        sweep_interval = int(sweep_interval * 1e9)
        for i in tqdm(range(num_sweep)):
            start_time = time.perf_counter_ns()
            trace = self.visa.sweep_and_get_trace()
            results[i] = trace
            timestamps[i] = time.perf_counter_ns()
            elapsed_time = timestamps[i] - start_time
            sleep_time = max(0, sweep_interval - elapsed_time)
            time.sleep(sleep_time * 1e-9)

        iterations_event.set()  # Signal that all iterations are completed