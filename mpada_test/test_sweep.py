import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd

def get_random_fig_base64(num_line=2):
    
    fig = plt.figure()
    tmp = BytesIO()
    data = get_random_data(num_line)
    f = data['FREQ']
    for i in range(num_line):
        s = data['S_{:}'.format(i)]
        # s = data[:,1+i]
        plt.plot(f, np.abs(s), label="sweep {:}".format(i))
    plt.legend()
    plt.title('this is a test image')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('magnitude')
    plt.tight_layout()
    fig.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')
    return encoded, data

def get_blank_fig_base64():
    fig = plt.figure()
    tmp = BytesIO()
    plt.xlabel('frequency (Hz)')
    plt.ylabel('magnitude')
    plt.tight_layout()
    fig.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')
    return encoded

def get_random_data(num_line):
    num_pt = 201
    data = list()
    # data.append(np.linspace(0, 100, num_pt))
    data = pd.DataFrame()
    data['FREQ'] = np.linspace(int(0.5e9), int(5e9), num_pt)
    for i in range(num_line):
        data['S_{:}'.format(i)] = np.random.randn(num_pt) + 1j*np.random.randn(num_pt)
        # data.append(np.random.randn(num_pt))
    return data