import pyftdi.ftdi.Ftdi as ftdi

class MyFtdi:
    def __init__(self):  
        self.dev = None
        print(ftdi.show_devices())

print(ftdi.show_devices())