import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def get_random_fig_base64(num_line=2):
    num_pt = 201
    fig = plt.figure()
    tmp = BytesIO()
    for i in range(num_line):
        f = np.linspace(0, 100, num_pt)
        s = np.random.randn(num_pt)
        plt.plot(f, s, label="sweep {:}".format(i))
    plt.legend()
    plt.title('this is a test image')
    plt.xlabel('frequency (Hz)')
    plt.ylabel('magnitude')
    plt.tight_layout()
    fig.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')
    return encoded

def get_blank_fig_base64():
    fig = plt.figure()
    tmp = BytesIO()
    plt.xlabel('frequency (Hz)')
    plt.ylabel('magnitude')
    plt.tight_layout()
    fig.savefig(tmp, format='png')
    encoded = base64.b64encode(tmp.getvalue()).decode('utf-8')
    return encoded