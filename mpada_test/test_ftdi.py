import sys
 
# setting path
sys.path.append('../mpada')

import ftdi_comm
from time import sleep

pin_name = ['GPIO0', 'GPIO1', 'GPIO2', 'GPIO3', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7']

pin_grp_1 = ['GPIO0', 'GPIO1', 'GPIO2']
pin_grp_2 = ['GPIO2', 'GPIO3', 'GPIO4']

def flashing_light(ftdi):
    while True:
        for p in pin_name:
            ftdi.digital_write(p, 1)
            sleep(0.2)
            ftdi.digital_write(p, 0)

def multi_pin_flashing(ftdi):
    counter = 0
    while counter < 1:
        # ftdi.digital_write_raw(0x0F)
        ftdi.digital_write(pin_grp_1, 1)
        sleep(1)
        # ftdi.digital_write_raw(0x00)
        ftdi.digital_write(pin_grp_1, 0)
        sleep(1)

        ftdi.digital_write(pin_grp_2, 1)
        sleep(1)
        ftdi.digital_write(pin_grp_2, 0)
        sleep(1)
        counter += 1

####
ftdi = ftdi_comm.MyFtdi()
# flashing_light(ftdi)
multi_pin_flashing(ftdi)
