from string import ascii_lowercase
import warnings, sys, os, yaml
import numpy as np
from mpada import vna_comm
from mpada import util_data
from mpada import ftdi_comm
import time
import asyncio
from tqdm import tqdm

class VnaSweep:
    def __init__(self, all_pair=False, config_file_name = 'config.yaml'):
        # attemp to load from sweep config from 'config.yaml' before using default settings
        print("Attempting to load sweep config file from '{:}'".format(config_file_name))
        print("===============================================")
        if os.path.exists(config_file_name):
            with open(config_file_name) as f:
                config_data = yaml.safe_load(f)
            self.freq_start = int(config_data['freq_start'])
            self.freq_stop = int(config_data['freq_stop'])
            self.num_pt = config_data['num_pt']
            self.config = dict()
            self.config['IF_BW'] = config_data['IF_BW']
            print("-> config loaded from {}".format(config_file_name))
        else:
            print("-> config file not presented! Using default value")
            self.freq_start = int(0.5e9)
            self.freq_stop = int(6e9)
            self.num_pt = int(201)
            self.config = dict()
            self.config['IF_BW'] = int(100e3)
        print("\tstart frequency: {} GHz".format(self.freq_start/1e9))
        print("\t stop frequency: {} GHz".format(self.freq_stop/1e9))
        print("\t    # of points: {}".format(self.num_pt))
        print("===============================================")

        self.all_pair = all_pair
        if all_pair:
            self.sweep_pair = [('TX_0', 'RX_0'), ('TX_1', 'RX_1'), ('TX_2', 'RX_2'), ('TX_0', 'RX_1'), ('TX_0', 'RX_2'), ('TX_1', 'RX_0'), ('TX_1', 'RX_2'), ('TX_2', 'RX_0'), ('TX_2', 'RX_1')]
        else:
            self.sweep_pair = [('TX_0', 'RX_0'), ('TX_1', 'RX_1'), ('TX_2', 'RX_2')]
        self.fig = None
        self.data = None
        self.vna = vna_comm.VnaVisa() # VNA instrument, vna_comm class
        self.mcu = ftdi_comm.MyFtdi()

    def get_info(self):
        print("\n=======================================================")
        print('VNA Sweep Settings:')
        print('- Start frequency: {:} GHz, Stop frequency: {:} GHz'.format(self.freq_start/1e9, self.freq_stop/1e9))
        print('- # of Sweep Data Points: {:}'.format(self.num_pt))
        print("=======================================================\n")

    def parse_sweep_post(self, form, ant_list):
        for key, val in form.items():
            if key == "is_sweep_opposite":
                self.get_sweep_pair_opp(ant_list)
            elif key == "freq_start":
                self.freq_start = int(1e9 * float(val))
            elif key == "freq_stop":
                self.freq_stop = int(1e9 * float(val))
            elif key == "num_pt":
                self.num_pt = int(val)
            else:
                print("Ignoring received key = {:}".format(key))
        self.get_info()

    # get ant pairs for opposite side sweeping,
    # note calling this method will overwrite existing sweep pair
    def get_sweep_pair_opp(self, ant_list):
        self.sweep_pair = []
        for tx, rx in zip(ant_list[0], ant_list[1]):
            self.sweep_pair.append((tx, rx))
        print(self.sweep_pair)

    # get sweep table
    def get_sweep_table(self):
        from flask import Markup
        num_sweep = len(self.sweep_pair)
        base_str = ""

        h_list = ["Sweep", "TX Selected", "RX Selected"]
        for h in h_list:
            base_str += "<tr>\n\t<th>{:}</th>\n".format(h)
            for i in range(num_sweep):
                if h == h_list[0]:
                    base_str += "\t<th>{:}</th>\n".format(i)
                elif h == h_list[1]:
                    base_str += "\t<td>{:}</td>\n".format(self.sweep_pair[i][0])
                else:
                    base_str += "\t<td>{:}</td>\n".format(self.sweep_pair[i][1])
            base_str += "</tr>\n"
        return Markup(base_str)

    # start sweeping
    def sweep(self, dict_ctl, demo=True):
        num_sweep = len(self.sweep_pair)

        MyData = util_data.Data(self)

        # iterate all sweep pairs
        for i in range(num_sweep):
            tx, rx = self.sweep_pair[i]
            print("======== Starting Sweep #{:}========".format(i))
            tx_gpio, tx_sig = self.get_gpio_and_signal(dict_ctl, tx)
            rx_gpio, rx_sig = self.get_gpio_and_signal(dict_ctl, rx)

            # control string for debug and/or mcu host
            tx_str = self.get_control_str(tx, tx_gpio, tx_sig)
            rx_str = self.get_control_str(rx, rx_gpio, rx_sig)
            print("{:}: {:}\n{:}: {:}".format(tx, tx_str, rx, rx_str))
            
            # for testing, show a randomly generated signal
            if demo:
                if self.mcu.connected:
                    try:
                        mcu = self.mcu
                        mcu.digital_write_high(tx_gpio + rx_gpio, tx_sig + rx_sig)
                        time.sleep(1) # protection time before init sweeping
                        mcu.reset()
                    except:
                        print("mcu set pin error")
                data_trace = np.random.randn(self.num_pt) + 1j*np.random.randn(self.num_pt)
                MyData.add_S_dec(data_trace, 'S_{:}'.format(i))
            else:
                if self.mcu.connected:
                    try:
                        mcu = self.mcu
                        mcu.digital_write_high(tx_gpio + rx_gpio, tx_sig + rx_sig)
                        time.sleep(0.3) # protection time before init sweeping
                    except:
                        warnings.warn("mcu set pin error")
                self.vna.auto_rescale()
                data_trace = self.vna.get_trace()
                MyData.add_S_raw(data_trace, 'S_{:}'.format(i)) 
                time.sleep(0.05)
                if self.mcu.connected:
                    try:
                        mcu.reset()
                    except:
                        warnings.warn("mcu set pin error")
            
            
            print("========== End of Sweep ==========".format(i))   

        # generate figure from data
        self.data = MyData
        self.fig = MyData.to_fig()
        # print(np.shape(self.data))

    ###############################
    ### sweep all pair
    def all_pair_sweep(self, dict_ctl, data=[], time_stamp=[], interval=0.1, num_min = 0.02, num_iter = None):
        print("Starting all pair sweep...")
        num_sweep = len(self.sweep_pair)        
        # self.vna.ins.write("DISP:WIND1:ENAB OFF")
        if not num_iter:
            T = max(0.05, interval)
            num_iter = int(60 * num_min / num_sweep / T)
        num_tol =  int(num_iter * num_sweep)
        data = [''] * num_tol
        time_stamp = [0] * num_tol
        time_dur = [0] * num_tol
        counter = 0
        self.vna.ins.query("*OPC?")
        for _ in tqdm(range(num_iter)):
            for i in range(num_sweep):
                # get tx, rx pin control
                tx, rx = self.sweep_pair[i]
                tic = time.time()
                # print(f"started at {tic}")
                d, ts = self.single_sweep(tx, rx, dict_ctl, interval)
                # print(counter, ": time needed = ", time.time() - tic)
                data[counter] = d
                time_dur[counter] = time.time() - tic
                time_stamp[counter] = ts
                counter += 1
                # time_stamp.append(time.time() - tic)
        curr_time = time.time()
        # self.vna.ins.write("DISP:WIND1:ENAB ON")
        return curr_time, time_dur, time_stamp, data

    def single_sweep(self, tx, rx, dict_ctl, interval):
        tic = time.time()

        mcu = self.mcu
        vna = self.vna.ins

        tx_gpio, tx_sig = self.get_gpio_and_signal(dict_ctl, tx)
        rx_gpio, rx_sig = self.get_gpio_and_signal(dict_ctl, rx)

        # set mcu and rf switch
        mcu.digital_write_high(tx_gpio + rx_gpio, tx_sig + rx_sig)
        time.sleep(1e-3) # protection time before init sweeping

        vna.write("SENS:SWE:MODE SING;*WAI")
        vna.write("CALC:DATA? SDATA")
        data = vna.read()
        # vna.query("*OPC?")                  
        mcu.reset()

        toc = time.time()
        time.sleep(max(0, interval - (toc - tic)))
        time_stamp = time.time()  

        return data, time_stamp

    ######
    def save_data(self):
        return self.data.to_csv()

    ####
    def init_vna(self):
        visa = self.vna
        visa.get_all_resource()
        if visa.get_instrument():
            visa.init_ins(self)
        else:
            print("instrument discovery error")

    ## apply calset
    def apply_vna_calset(self, name='MPADA'):
        print("Loading calset '{}'...".format(name))
        self.vna.apply_calset(name)        

    ####
    def reset_vna(self):
        visa = self.vna
        visa.get_all_resource()
        if visa.get_instrument():
            # visa.init_ins(self)
            self.vna.soft_reset(self)
        else:
            print("instrument discovery error")            

    #####
    def get_gpio_and_signal(self, dict_ctl, ant):
        return dict_ctl[ant][0], dict_ctl[ant][1]

    def get_control_str(self, ant, gpio, sig):
        base_str = ""
        for g, s in zip(gpio, sig):
            base_str += "{:}={:} ".format(g, s)
        return base_str


####
class VnaSweepConfig(VnaSweep):
    def __init__(self):
        pass

    def set_freq(self, f_start, f_stop, num_pt, **kwargs):
        self.freq_start = int(f_start)
        self.freq_stop = int(f_stop)
        self.num_pt = int(num_pt)
        self.config = kwargs
        if 'IF_BW' not in self.config:
            self.config['IF_BW'] = int(100e3)