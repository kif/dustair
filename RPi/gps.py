#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the GPS reciever

from collections import namedtuple
import time
import threading
import logging
import serial 
import pynmea2
logger = logging.getLogger(__name__)
Position = namedtuple("Position", ["lat_dir", "lat", "lon_dir", "lon" ])

class GPS(threading.Thread):
    "A class recieving continusly  GPS data and serving the latest ones"
    def __init__(self, port="/dev/ttyAMA0", quit_event=None):
        self.gps = serial.Serial(port)
        self.stream = pynmea2.NMEAStreamReader(self.gps)
        self.date = None
        self.time = None
        self.position = None
        if quit_event is not None:
            self.quit_event = quit_event
        else:
            self.quit_event = threading.Event()
        threading.Thread.__init__(self, name="GPS")

    def run(self):
        "poll the device"
        while not self.quit_event.is_set():
            try:
                for msg in self.stream.next():
                    name = msg.__class__.__name__
                    if  name == "RMC":
                        self.date = msg.datestamp
                    if name in ("GGA", "GLL", "RMC"):
                        self.time = msg.timestamp
                        try:
                            self.position = Position(msg.lat_dir, float(msg.lat), msg.lon_dir, float(msg.lon))
                        except Exception as e:
                            logger.info("%s: %s, %s",e.__class__.__name__, e, msg)
                    
            except pynmea2.nmea.ParseError as e:
                logger.info("ParseError: %s", e)
                
    def get(self, what=None):
        if what == "header":
            return "  Latitude  Longitude"
        elif what == "unit":
            return Position("lat_dir", "lat", "lon_dir", "lon")
        elif what == "text":
            if self.position:
                return "%1s%9.4f %1s%9.4f"%self.position
        else:
            return self.position
