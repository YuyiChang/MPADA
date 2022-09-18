import numpy as np

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


