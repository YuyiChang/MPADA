# VNA simulator for MPADA demo
from typing import Any
from mpada.vna_comm import VnaVisa
import numpy as np
from mpada.vna_sweep import VnaSweepConfig

class DemoInstrument():
    def __init__(self) -> None:
        pass

    def write(self, input):
        print("demo visa write: ", input)
    
    def read(self):
        return "1 2 3 4 5 6"
    
    def querry(self):
        return self.read()
    

class DemoVisa():
    def __init__(self) -> None:
        self.ins = DemoInstrument()
        self.vna_sweep = VnaSweepConfig()
        self.vna_sweep.set_freq(f_start=0.5*1e9, 
                                 f_stop=6.0*1e9, 
                                 num_pt=201)

    def get_all_resource(self):
        return ["DEMO::0.0.0.0::INSTR", "DEMO::0.0.0.1::INSTR"]
    
    def connect_instrument(self, device):
        device_name = "MPADA v2, Demo VNA"
        return device_name
    
    def init_ins(self, vna_sweep, port_name='S12'):
        self.vna_sweep = vna_sweep

    def get_freq(self):
        return f"f_start: {self.vna_sweep.freq_start}\n \
    f_stop: {self.vna_sweep.freq_stop}\n \
    num_pt: {self.vna_sweep.num_pt}"

    def __getattr__(self, *arg):
        pass

    def sweep_and_get_trace(self):
        data = np.random.rand(self.vna_sweep.num_pt) + 1.j * np.random.rand(self.vna_sweep.num_pt)
        return data
    
    # def process_trace(self, trace):
    #     data = np.fromstring(trace, sep=',')
    #     data = data[::2] + 1j*data[1::2]
    #     return data
    
