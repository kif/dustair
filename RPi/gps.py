#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the GPS reciever

from collections import namedtuple
import time
import threading
import serial, pynmea2
Position = namedtuple("Position", ["lat", "lat_dir", "lon", "lon_dir"])

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
        threading.Thread.__init__(self, name="DHT")

    def run(self):
        "poll the device"
        while not self.quit_event.is_set():
            try:
                for msg in self.stream.next():
                    if msg.__class__.__name__ == "RMC":
                        self.date = msg.datestamp
                        self.time = msg.timestamp
                        self.position = Position(msg.lat_dir, float(msg.lat), msg.lon_dir, float(msg.lon))
            except ParseError as e:
                logger.info("ParseError %s", e)
                
            if (values[0] or values[1]) is not None:
                self.last_value = HumidityTemparture(*values)

gps = serial.Serial('/dev/ttyAMA0')
streamreader = pynmea2.NMEAStreamReader(gps)
valid = ["GGA", "ZDA","GLL"]
while 1:
        for msg in streamreader.next():
                    if msg.__class__.__name__ in valid:
                                    print(msg)
                                    while 1:
                                            for msg in streamreader.next():
                                                        if msg.__class__.__name__ in valid:
                                                                        print(msg)
                                                                        %histor
                                                                        %history

