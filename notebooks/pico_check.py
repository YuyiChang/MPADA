# %%
import hid
hid.enumerate()
'device' in dir(hid)


import serial.tools.list_ports as lp
lp.comports()

# %%
import hid

device = hid.device()
device.open(0xCAFE, 0x4005)
device.close()

# %%

import os
os.environ["BLINKA_U2IF"] = "1"
# %%
import board

dir(board)

# %%



import time
import board
import digitalio

led = digitalio.DigitalInOut(board.GP17)
led.direction = digitalio.Direction.OUTPUT

while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
    