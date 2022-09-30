import numpy as np
from flask import Markup
from mpada import vna_comm
from mpada import util_data
import time

class VnaSweep:
    def __init__(self):
        self.freq_start = int(0.5e9)
        self.freq_stop = int(6e9)
        self.num_pt = int(201)
        self.sweep_pair = [('TX_0', 'RX_0'), ('TX_1', 'RX_1'), ('TX_2', 'RX_2')]
        self.fig = None
        self.data = None
        self.vna = vna_comm.VnaVisa() # VNA instrument, vna_comm class

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
        def get_gpio_and_signal(dict_ctl, ant):
            return dict_ctl[ant][0], dict_ctl[ant][1]

        def get_control_str(ant, gpio, sig):
            base_str = ""
            for g, s in zip(gpio, sig):
                base_str += "{:}={:} ".format(g, s)
            return base_str

        num_sweep = len(self.sweep_pair)

        MyData = util_data.Data(self)

        # iterate all sweep pairs
        for i in range(num_sweep):
            tx, rx = self.sweep_pair[i]
            print("======== Starting Sweep #{:}========".format(i))
            tx_gpio, tx_sig = get_gpio_and_signal(dict_ctl, tx)
            rx_gpio, rx_sig = get_gpio_and_signal(dict_ctl, rx)

            # control string for debug and/or mcu host
            tx_str = get_control_str(tx, tx_gpio, tx_sig)
            rx_str = get_control_str(rx, rx_gpio, rx_sig)
            print("{:}: {:}\n{:}: {:}".format(tx, tx_str, rx, rx_str))
            
            # TODO: set control signal to VNA and MCU
            # for testing, show a randomly generated signal
            if demo:
                data_trace = np.random.randn(self.num_pt) + 1j*np.random.randn(self.num_pt)
                MyData.add_S_dec(data_trace, 'S_{:}'.format(i))
            else:
                self.vna.auto_rescale()
                data_trace = self.vna.get_trace()
                MyData.add_S_raw(data_trace, 'S_{:}'.format(i)) 
                time.sleep(0.05)
            
            
            print("========== End of Sweep ==========".format(i))   

        # generate figure from data
        self.data = MyData
        self.fig = MyData.to_fig()
        # print(np.shape(self.data))

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

    ####
    def reset_vna(self):
        if self.vna.ins:
            self.vna.soft_reset(self)


