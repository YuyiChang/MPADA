# %%
import serial
import serial.tools.list_ports
for a in list(serial.tools.list_ports.comports()):
    print(a)


# %%
port = 'COM21'
ser = serial.Serial(timeout=5, baudrate=9600)
ser.port = port