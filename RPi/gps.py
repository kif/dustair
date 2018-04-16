#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the GPS reciever

from collections import namedtuple
import time
import threading
import logging
import serial 
import pynmea2
logger = logging.getLogger(__name__)
Position = namedtuple("Position", ["Latitude", "Longitude" ])

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
                        lat = lon = None
                        if msg.lat:
                            try:
                                lat = int(msg.lat[:2]) + float(msg.lat[2:])/60.
                            except Exception as e:
                                logger.info("%s: %s, %s",e.__class__.__name__, e, msg)
                                continue
                            if msg.lat_dir == "S":
                                lat = -lat
                        if msg.lon:
                            try:
                                lon = int(msg.lon[:3]) + float(msg.lon[3:])/60.
                            except Exception as e:
                                logger.info("%s: %s, %s",e.__class__.__name__, e, msg)
                                continue
                            if msg.lon_dir == "W":
                                lon = -lon
                        if lat and lon:
                            self.position = Position(lat, lon)
                    
            except pynmea2.nmea.ParseError as e:
                logger.info("ParseError: %s", e)
                
    def get(self, what=None):
        if what == "header":
            return "  Latitude  Longitude"
        elif what == "unit":
            return Position("degree", "degree")
        elif what == "text":
            if self.position:
                return "%10.6f %10.6f"%self.position
        else:
            return self.position

