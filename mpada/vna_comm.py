import pyvisa
import time
import os

class VnaVisa:
    def __init__(self):
        # io driver directory
        if os.name == 'nt':
            # os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\')
            self.dir_io = ''
        elif os.name == 'posix':
            self.dir_io = '/opt/keysight/iolibs/libktvisa32.so' 
        else:
            EnvironmentError("unsupported OS: {:}".format(os.name))
        
        # VISA resource manager
        self.rm = None
        # my instrument
        self.ins = None

    # get all avaliale instruments
    def get_all_resource(self):
        self.rm = pyvisa.ResourceManager(self.dir_io)
        rest_list = self.rm.list_resources() # show all equipments
        print("Resource found: ", rest_list)

    # get instrument from resource list
    def get_instrument(self, index=0):
        rest_list = self.rm.list_resources() # show all equipments
        if len(rest_list) > 0:
            print("selecting instrument #{:}".format(index))
            print(rest_list[index])
            self.ins = self.rm.open_resource(rest_list[index])
            print(self.ins.query('*IDN?'))
            return True
        else:
            print("resource list empty, no instrument to select!")
            return False
        

    # init/reset instrument
    def init_ins(self, vna_sweep, port_name='S12'):
        ins = self.ins
        # set timeout to 5s
        ins.timeout = 5000

        # present VNA and wait for preset completion via OPC
        ins.write("SYST:FPReset;*OPC?")
        ins.read()
        # clear event status registers and empty the error queue
        ins.write("*CLS")
        # init display window
        ins.write("DISP:WIND1:STATE ON")
        # use S12 measurement
        ins.write("CALC:PAR:DEF:EXT '{:}', {:}".format(port_name, port_name))
        # attach S12 measurement to display window
        ins.write("DISP:WIND1:TRAC:FEED 'S12'")
        
        ## set start/end freq and number of trace points
        # set number of points
        ins.write("SENS:SWE:POIN " + str(vna_sweep.num_pt) + ";*OPC?")
        ins.read()

        # set start and ending freq
        ins.write("SENS:FREQ:STAR " + str(vna_sweep.freq_start))
        ins.write("SENS:FREQ:STOP " + str(vna_sweep.freq_stop))

        # set trigger mode to continuous
        ins.write("SENS:SWE:MODE CONT;*OPC?") # continuous trigger
        ins.read()
   
   
    # soft reset/init
    def soft_reset(self, vna_sweep):
        ins = self.ins
        ins.write("*CLS")
        ## set start/end freq and number of trace points
        # set number of points
        ins.write("SENS:SWE:POIN " + str(vna_sweep.num_pt) + ";*OPC?")
        ins.read()

        # set start and ending freq, and sweep mode
        ins.write("SENS:FREQ:STAR " + str(vna_sweep.freq_start))
        ins.write("SENS:FREQ:STOP " + str(vna_sweep.freq_stop))
        ins.write("SENS:SWE:MODE CONT;*OPC?")
        ins.read()
        
    # get trace data in string format
    def get_trace(self):
        self.ins.write("CALC:DATA? SDATA")
        return self.ins.read()
    
    def auto_rescale(self):
        self.ins.write("DISP:WIND:TRAC:Y:AUTO")