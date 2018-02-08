#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the SDS dust sensor

from collections import namedtuple
import time
import threading
import logging
import serial 
import pynmea2
logger = logging.getLogger(__name__)
Dust = namedtuple("Dust", ["PM2_5", "PM10"])

class SDS(threading.Thread):
    "A class recieving continusly dust-sensor data and serving the latest ones"
    def __init__(self, port="/dev/ttyUSB0", quit_event=None):
        self.sensor = serial.Serial(port)
        if quit_event is not None:
            self.quit_event = quit_event
        else:
            self.quit_event = threading.Event()
        self.last_value = None
        threading.Thread.__init__(self, name="SDS")

    def run(self):
        "poll the device"
        while not self.quit_event.is_set():
            raw = self.sensor.read(10)
            
            if len(raw) == 10:
                dec = [int(i) for i in raw]
                valid = ((dec[0] == 170) and
                         (dec[1] == 192) and
                         (dec[9] == 171))
                if valid:
                    if (sum(dec[2:8])%256 == dec[8]):
                        self.last_value = Dust((dec[2] + dec[3]*256)/10., 
                                               (dec[4] + dec[5]*256)/10.)
                else:
                    logger.warning("Checksum error")
            else:
                valid = False
            if not valid:
                logger.warning("Invalid datagram: %s", [int(i) for i in raw])
                #Read until next \xaa
                ch = self.sensor.read(1)
                while ch != b"\xaa":
                    ch = self.sensor.read(1)
                self.sensor.read(9)

    def get(self, what=None):
        if what == "header":
            return " PM2.5   PM10"
        elif what == "unit":
            return "Dust", ["PM2.5 (µg/m³)", "PM10 (µg/m³)"]
        elif what == "text":
            if self.last_value:
                return "%6.1f %6.1f"%self.last_value
        else:
            return self.last_value
        
