#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the SDS dust sensor
import glob
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
    def __init__(self, port="/dev/ttyUSB", quit_event=None):
        self.port = port
        self.actual_port = None
        self.sensor = None
        self.set_port(port)
        if quit_event is not None:
            self.quit_event = quit_event
        else:
            self.quit_event = threading.Event()
        self.last_value = None
        threading.Thread.__init__(self, name="SDS")

    def set_port(self, port=None):
        "set the sensor to the opened port"
        if port is None:
            port = self.port
        actual_port = glob.glob(port+"*")
        actual_port.sort()
        if not actual_port: 
            if self.sensor is not None:
                logger.warning("Disabling %s", self.actual_port)
                self.sensor.close()
                self.sensor = None
            self.actual_port = None
            return False
        if actual_port[-1] != self.actual_port:
            logger.warning("Switching from %s to %s", self.actual_port, actual_port)
            if self.sensor is not None:
                self.sensor.close()
            self.actual_port = actual_port[-1]
            self.sensor = serial.Serial(self.actual_port)
            return True

    def parse(self, raw):
        "parse a datagram, sets the value and returns True when OK"
        if len(raw) == 10:
            dec = [int(i) for i in raw]
            valid = ((dec[0] == 170) and
                     (dec[1] == 192) and
                     (dec[9] == 171))
            if valid:
                if (sum(dec[2:8])%256 == dec[8]):
                    self.last_value = Dust((dec[2] + dec[3]*256)/10., 
                                           (dec[4] + dec[5]*256)/10.)
                    return True
            else:
                logger.warning("Checksum error")
                return
        else:
            return False

    def run(self):
        "poll the device"
        while not self.quit_event.is_set():
            if self.set_port() is False:
                time.sleep(1)
                continue

            try:
                raw = self.sensor.read(10)
            except:
                continue
            valid = self.parse(raw)
            if valid is False:
                logger.warning("Invalid datagram: %s", [int(i) for i in raw])
                #Read until next \xaa
                ch = self.sensor.read(1)
                while ch != b"\xaa":
                    ch = self.sensor.read(1)
                self.parse(ch+self.sensor.read(9))

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
        
