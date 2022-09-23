import pyvisa
import time

class VnaVisa:
    def __init__(self):
        # io driver directory
        self.dir_io = '/opt/keysight/iolibs/libktvisa32.so' 
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
        else:
            print("resource list empty, no instrument to select!")

    # init/reset instrument
    def init_ins(self, vna_sweep, port_name="S12"):
        ins = self.ins
        # set timeout to 5s
        ins.timeout = 5000

        # preset the PNA and wait for preset completion via OPC
        ins.write("SYST:PRES;*OPC?")
        ins.read()

        # clear event status registers and empty the error queue
        ins.write("*CLS")

        ## set ch and trace to S12 by default
        # select default measurement name
        ins.write("CALC:PAR:SEL 'CH1_S11_1'")
        # set data tranfer format to ASCII
        ins.write("FORM:DATA ASCII")
        # alter measure from S11 to S21
        ins.write("CALC:PAR:MOD {:}".format(port_name))

        ## set start/end freq and number of trace points
        # set number of points
        ins.write("SENS:SWE:POIN " + str(vna_sweep.num_pt) + ";*OPC?")
        ins.read()

        # set start and ending freq
        ins.write("SENS:FREQ:STAR " + str(vna_sweep.freq_start))
        ins.write("SENS:FREQ:STOP " + str(vna_sweep.freq_stop))
   
   
    # soft reset/init
    def soft_reset(self, vna_sweep):
        ins = self.ins
        ## set start/end freq and number of trace points
        # set number of points
        ins.write("SENS:SWE:POIN " + str(vna_sweep.num_pt) + ";*OPC?")
        ins.read()

        # set start and ending freq
        ins.write("SENS:FREQ:STAR " + str(vna_sweep.freq_start))
        ins.write("SENS:FREQ:STOP " + str(vna_sweep.freq_stop))
        

    
