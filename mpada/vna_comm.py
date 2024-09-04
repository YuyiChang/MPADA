import pyvisa
import time
import os
import numpy as np

class VnaVisa:
    def __init__(self, backend=None):
        # io driver directory
        if backend is None:
            if os.name == 'nt':
                # os.add_dll_directory('C:\\Program Files\\Keysight\\IO Libraries Suite\\')
                self.dir_io = ''
            elif os.name == 'posix':
                self.dir_io = '/opt/keysight/iolibs/libktvisa32.so' 
            else:
                EnvironmentError("unsupported OS: {:}".format(os.name))
        else:
            self.dir_io = backend

        # VISA resource manager
        self.rm = None
        # my instrument
        self.ins = None

    # get all avaliale instruments
    def get_all_resource(self):
        self.rm = pyvisa.ResourceManager(self.dir_io)
        rest_list = self.rm.list_resources() # show all equipments
        print("Resource found: ", rest_list)
        return rest_list
    
    # connect to vna device
    def connect_instrument(self, device):
        try:
            self.ins = self.rm.open_resource(device)
            return self.ins.query('*IDN?')
        except Exception as e:
            return str(e)

    # DEPRECATED: get instrument from resource list
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
        # # attach S12 measurement to display window
        ins.write("DISP:WIND1:TRAC:FEED 'S12'")
        
        ## set start/end freq and number of trace points
        # set number of points
        ins.write("SENS:SWE:POIN " + str(vna_sweep.num_pt) + ";*OPC?")
        ins.read()

        # set start and ending freq
        ins.write("SENS:FREQ:STAR " + str(vna_sweep.freq_start))
        ins.write("SENS:FREQ:STOP " + str(vna_sweep.freq_stop))

        # set IF BW
        ins.write("SENSE:BWID " + str(vna_sweep.config['IF_BW']))


        # print config
        print("Freq start: " + ins.query("SENS:FREQ:STAR?"))
        print("Freq stop: " + ins.query("SENS:FREQ:STOP?"))
        print("IF BW: ", ins.query("SENSE:BWID?"))

        # set trigger mode to continuous
        ins.write("SENS:SWE:MODE SING;*OPC?") # continuous trigger
        ins.read()
        

    def get_freq(self):
        ins = self.ins
        f_start = f"Freq start: {ins.query('SENS:FREQ:STAR?')}\n"
        f_stop = f"Freq stop: {ins.query('SENS:FREQ:STOP?')}\n"
        return f_start + f_stop

   
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

    def sweep_and_get_trace(self):
        self.ins.write("SENS:SWE:MODE SING;*WAI")
        self.ins.write("CALC:DATA? SDATA")
        data = self.ins.read()
        data = self.process_trace(data)

        return data
    
    def process_trace(self, trace):
        data = np.fromstring(trace, sep=',')
        data = data[::2] + 1j*data[1::2]
        return data
        
    # get trace data in string format
    def get_trace(self):
        self.ins.write("CALC:DATA? SDATA")
        return self.ins.read()
    
    def auto_rescale(self):
        self.ins.write("DISP:WIND:TRAC:Y:AUTO")

    def apply_calset(self, name='MPADA'):
        self.ins.write("SENS:CORR:CSET:ACT '{}', 1".format(name))

    def display_off(self):
        # self.ins.write("DISP:WIND:ENABle OFF")
        self.ins.write("DISP:WIND:TRAC:DEL")
        self.ins.query("*OPC?")

    def display_on(self):
        # self.ins.write("DISP:WIND:ENABle ON")
        self.ins.write("DISP:WIND1:TRAC:FEED 'S12'")

    def calibration(self, name="MPADA"):
        ins = self.ins
        ins.write("CALC:PAR:SEL 'S12'")

        # get existing calset
        avai_calset = ins.query("SENS:CORR:CSET:CAT? NAME")

        #### setup guided E-CAL

        # print(ins.query("SENS:CORR:COLL:GUID:CONN:CAT?"))
        ins.write("SENS:CORR:COLL:GUID:CONN:PORT1 'APC 3.5 male'")
        ins.write("SENS:CORR:COLL:GUID:CONN:PORT2 'APC 3.5 male'")

        # print(ins.query("SENS:CORR:COLL:GUID:CKIT:PORT:CAT?"))
        ins.write("SENS:CORR:COLL:GUID:CKIT:PORT1 'N4691-60005 ECal'")
        ins.write("SENS:CORR:COLL:GUID:CKIT:PORT2 'N4691-60005 ECal'")

        if name in avai_calset:
            print("CalSet with name '{}' already exists, overwriting...".format(name))
            print("Found the following calsets: " + ins.query("SENS:CORR:CSET:CAT? NAME"))
            ins.write("SENS:CORR:COLL:GUID:INIT '{}'".format(name))    
        else:
            ins.write("SENS:CORR:COLL:GUID:INIT")
        ####

        ### perform each cal step
        num_step = int(ins.query("SENS:CORR:COLL:GUID:STEPS?"))
        print("num of step = {}".format(num_step))

        for i in range(1, num_step+1):
            print("Performing step {} of {}".format(i, num_step))
            print(ins.query("sens:corr:coll:guid:desc? {}".format(i)))
            input("Press any key to continue...")
            ins.write("sens:corr:coll:guid:acq STAN{}".format(i))
        ####

        ins.query("*OPC?")

        ### Save calibration results
        ins.write("SENS:CORR:PREF:CSET:SAVE USER")
        ins.write("SENS:CORR:COLL:GUID:SAVE")
        ins.write("SENS:CORR:CSET:NAME '{}'".format(name))

        print("\nCalibration completed. CalSet has been saved as '{}'".format(name))
        print(ins.query("SENS:CORR:CSET:CAT? NAME"))

