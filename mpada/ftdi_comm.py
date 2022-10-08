from pyftdi.gpio import GpioAsyncController
from pyftdi.ftdi import Ftdi as ftdi

class MyFtdi:
    def __init__(self):  
        self.gpio = GpioAsyncController()
        self.connected = False
        self.pin_state = 0x00
        self.pin_map = {
            'GPIO0': 0x01,
            'GPIO1': 0x02,
            'GPIO2': 0x04,
            'GPIO3': 0x08,
            'GPIO4': 0x10,
            'GPIO5': 0x20,
            'GPIO6': 0x40,
            'GPIO7': 0x80
        }
        print(ftdi.show_devices())
        try:
            # attempt to connect any ftdi device connected, set all pin to output mode
            self.gpio.configure('ftdi:///1', direction=0xFF)
            self.reset()
            self.connected = True
        except:
            print("Connection failed. Is FTDI plugged in?")

    # mode: 1 (HIGH), 0 (LOW)
    def digital_write_high(self, pin, mode) -> None:
        if isinstance(pin, str):
            pin = [pin]
        if isinstance(mode, int) or isinstance(mode, str) :
            mode = [mode]

        for p, mode in zip(pin, mode):
            mode = int(mode)
            # set high
            if mode == 1:
                self.pin_state |= self.pin_map[p]
        print(bin(self.pin_state))
        self.gpio.write(self.pin_state)

    def digital_write_raw(self, pin_raw):
        self.gpio.write(pin_raw)

    # reset all pin
    def reset(self) -> None:
        self.gpio.write(0x00)
        self.pin_state = 0x00


    
