# %%
import sys
# setting path
sys.path.append('../mpada')

import ftdi_comm
from time import sleep

pin_name = ['GPIO0', 'GPIO1', 'GPIO2', 'GPIO3', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7']

pin_grp_1 = ['GPIO0', 'GPIO1', 'GPIO2']
pin_grp_2 = ['GPIO2', 'GPIO3', 'GPIO4']

def flashing_all(ftdi):
    while True:
        # ftdi.digital_write_high(p, 1)
        ftdi.digital_write_raw(0xFF)
        sleep(0.2)
        # ftdi.digital_write_high(p, 0)
        ftdi.reset()
        sleep(0.2)

def flashing_light(ftdi):
    while True:
        for p in pin_name:
            print(p)
            # ftdi.digital_write_high(p, 1)
            ftdi.digital_write_raw(0xFF)
            sleep(0.2)
            # ftdi.digital_write_high(p, 0)
            ftdi.reset()
            sleep(0.2)

def multi_pin_flashing(ftdi):
    counter = 0
    while counter < 10:
        print(counter)
        # ftdi.digital_write_raw(0x0F)
        ftdi.digital_write_high(pin_grp_1, [1, 0, 1])
        sleep(1)
        # ftdi.digital_write_raw(0x00)
        # ftdi.digital_write(pin_grp_1, 0)
        ftdi.reset()
        sleep(1)

        ftdi.digital_write_high(pin_grp_2, [1, 1, 0])
        sleep(1)
        ftdi.reset()
        counter += 1

def sequential_flash(ftdi):
    pin_map = {
            'GPIO0': 0x01,
            'GPIO1': 0x02,
            'GPIO2': 0x04,
            'GPIO3': 0x08,
            'GPIO4': 0x10,
            'GPIO5': 0x20,
            'GPIO6': 0x40,
            'GPIO7': 0x80
        }
    while True:
        for v in pin_map.values():
            ftdi.digital_write_raw(v)
            sleep(0.2)
            ftdi.reset()
            sleep(0.2)


####
ftdi = ftdi_comm.MyFtdi()
sequential_flash(ftdi)
# flashing_all(ftdi)
# multi_pin_flashing(ftdi)
