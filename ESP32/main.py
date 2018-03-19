# Main program executed by micropython

import os, time, machine
from gps import GPS

led = machine.Pin(16, machine.Pin.OUT)
gps = GPS(2, 9600, led=led)
# for i in range(1000):
#     gps.update()
#     time.sleep(1000)

# TODO: use timer
# from machine import Timer
#
timer = machine.Timer(-1)
timer.init(period=1000,  # every second
           mode=machine.Timer.PERIODIC,
           callback=lambda t:gps.quick_update())
