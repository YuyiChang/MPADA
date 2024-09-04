import os
os.environ["BLINKA_U2IF"] = "1"

import time
import board
import digitalio

led = digitalio.DigitalInOut(board.GP17)
led.direction = digitalio.Direction.OUTPUT

# print(dir(board))

# init GPIOs
pin_list = []
for i in range(6):
    pin = digitalio.DigitalInOut(eval(f'board.GP{i}'))
    pin.direction = digitalio.Direction.OUTPUT
    pin_list.append(pin)

while True:
    for pin in pin_list:
        pin.value = True
        time.sleep(1)
        pin.value = False
        