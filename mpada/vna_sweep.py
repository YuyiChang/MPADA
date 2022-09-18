import numpy as np
from flask import Markup

class VnaSweep:
    def __init__(self):
        self.freq_start = int(0.5e9)
        self.freq_stop = int(6e9)
        self.num_pt = int(401)
        self.sweep_pair = [('TX_0', 'RX_0'), ('TX_1', 'RX_1'), ('TX_2', 'RX_2')]

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

        for h in ["Sweep", "TX Selected", "RX Selected"]:
            base_str += "<tr>\n\t<th>{:}</th>\n".format(h)
            for i in range(num_sweep):
                if h == "Sweep":
                    base_str += "\t<th>{:}</th>\n".format(i)
                elif h == "TX":
                    base_str += "\t<td>{:}</td>\n".format(self.sweep_pair[i][0])
                else:
                    base_str += "\t<td>{:}</td>\n".format(self.sweep_pair[i][1])
            base_str += "</tr>\n"
        return Markup(base_str)

    # start sweeping
    def sweep(self, dict_ctl):
        def get_gpio_and_signal(dict_ctl, ant):
            return dict_ctl[ant][0], dict_ctl[ant][1]

        def get_control_str(ant, gpio, sig):
            base_str = ""
            for g, s in zip(gpio, sig):
                base_str += "{:}={:} ".format(g, s)
            return base_str
            
        num_sweep = len(self.sweep_pair)
        for i in range(num_sweep):
            tx, rx = self.sweep_pair[i]
            print("======== Starting Sweep #{:}========".format(i))
            tx_gpio, tx_sig = get_gpio_and_signal(dict_ctl, tx)
            rx_gpio, rx_sig = get_gpio_and_signal(dict_ctl, rx)

            tx_str = get_control_str(tx, tx_gpio, tx_sig)
            rx_str = get_control_str(rx, rx_gpio, rx_sig)

            # TODO: set control signal to VNA and MCU
            # for testing, show a randomly generated signal
            
            print("{:}: {:}\n{:}: {:}".format(tx, tx_str, rx, rx_str))
            print("========== End of Sweep ==========".format(i))


