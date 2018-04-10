# Main program executed by micropython

from machine import Timer, Pin
from gps import GPS
from sds import SDS

led = Pin(16, Pin.OUT)
led.value(0)
gps = GPS(2, 9600)
sds = SDS(1)

def update_all(*arg, **kwarg):
    led.value(1)
    sds.update()
    gps.update()
    led.value(0)

update_all()

timer = Timer(-1)
timer.init(period=1000,  # every second
           mode=Timer.PERIODIC,
           callback=update_all)
