# Main program executed by micropython

from machine import Timer
from gps import GPS
from sds import SDS
# led = machine.Pin(16, machine.Pin.OUT)
# led.value(0)
gps = GPS(2, 9600)
sds = SDS(1)


timer_gps = Timer(-1)
timer_gps.init(period=1000,  # every second
               mode=Timer.PERIODIC,
               callback=lambda t: [i.quick_update() for i in (gps, sds)]
               )
