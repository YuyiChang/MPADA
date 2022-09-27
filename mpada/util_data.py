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
        S = self.parse_raw_S(trace_data)
        self.data[name] = S

    def add_S_dec(self, trace_data, name):
        self.data[name] = trace_data

    # parse VNA returned S data to numpy array
    def parse_raw_S(self, trace_data):
        return np.fromstring(trace_data, sep=',')

    def to_fig(self):
        fig = plt.figure()
        tmp = BytesIO()
        data = self.data
        f = data['FREQ']
        num_sweep = np.shape(data)[1]-1
        for i in range(num_sweep):
            s = data['S_{:}'.format(i)]
            plt.plot(f, np.abs(s), label="sweep {:}".format(i))
        plt.legend()
        plt.title('this is a test image')
        plt.xlabel('frequency (Hz)')
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