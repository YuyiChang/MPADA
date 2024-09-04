import matplotlib as mpl
mpl.use('Agg')
import pandas as pd
import tempfile
import numpy as np
from io import BytesIO
import base64
import matplotlib.pyplot as plt

class Data:
    def __init__(self, VnaSweepSpec):
        self.data = pd.DataFrame()
        self.data['FREQ'] = np.linspace(VnaSweepSpec.freq_start, VnaSweepSpec.freq_stop, VnaSweepSpec.num_pt)

    def add_S_raw(self, trace_data, name):
        data = self.parse_raw_S(trace_data)
        self.data[name] = data[::2] + 1j*data[1::2]

    def add_S_dec(self, trace_data, name):
        self.data[name] = trace_data

    # parse VNA returned S data to numpy array
    def parse_raw_S(self, trace_data):
        return np.fromstring(trace_data, sep=',')

    def to_fig(self, use_db=True):
        fig = plt.figure()
        tmp = BytesIO()
        data = self.data
        f = data['FREQ']
        num_sweep = np.shape(data)[1]-1
        for i in range(num_sweep):
            s = data['S_{:}'.format(i)]
            if use_db:
                plt.plot(f, 20*np.log10(np.abs(s)), label="sweep {:}".format(i))
            else:
                plt.plot(f, np.abs(s), label="sweep {:}".format(i))
        plt.legend()
        # plt.title('Collected Data')
        plt.xlabel('frequency (Hz)')
        if use_db:
            plt.ylabel('magnitude (dB)')
        else:
            plt.ylabel('magnitude')
        plt.tight_layout()
        fig.savefig(tmp, format='png')
        encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')
        return encoded

    def to_csv(self):
        f = tempfile.TemporaryFile()
        self.data.to_csv(f)
        f.seek(0)
        return f


def hello_message():
    print(r"""
         __  __ ____   _    ____    _      _ _ _       
        |  \/  |  _ \ / \  |  _ \  / \    | (_) |_ ___ 
        | |\/| | |_) / _ \ | | | |/ _ \   | | | __/ _ \
        | |  | |  __/ ___ \| |_| / ___ \  | | | ||  __/
        |_|  |_|_| /_/   \_\____/_/   \_\ |_|_|\__\___|
                                                        
    """)
    print("Welcome to MPADA lite! by Yuyi (chang.1560@osu.edu)\n")

def get_stats(t):
    t = np.array(t) * 1e3
    stats = [len(t), np.min(t), np.max(t), np.mean(t), np.std(t), np.median(t)]
    print("# sample = {}, min = {:.2f}, max = {:.2f}, mean = {:.2f}, stdev = {:.2f}, median = {:.2f}".format(stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]))
    return stats