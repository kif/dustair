#!/home/jerome/py3/bin/python3

# Simple module for reading continuously the temperature and the humidity

from collections import namedtuple
import time
import threading
import Adafruit_DHT

HumidityTemparture = namedtuple("HT", ["Humidity", "Temperature"])

class DHT(threading.Thread):
    "A polling class which always provides you with temperature/humidity"
    def __init__(self, pin=23, delay=2, sensor=Adafruit_DHT.DHT22, quit_event=None):
        self.pin = pin
        self.delay = delay
        self.sensor = sensor
        self.last_value = None
        if quit_event is not None:
            self.quit_event = quit_event
        else:
            self.quit_event = threading.Event()
        threading.Thread.__init__(self, name="DHT")

    def run(self):
        "poll the device"
        while not self.quit_event.is_set():
            values = Adafruit_DHT.read(self.sensor, self.pin)
            if (values[0] or values[1]) is not None:
                self.last_value = HumidityTemparture(*values)
            time.sleep(self.delay)
            
    def get(self, what=None):
        if what == "header":
            return "Humidity Temperature"
        elif what == "unit":
            return HumidityTemparture("%", "°C")
        elif what == "text":
            return "   %5.1f      %6.1f"%self.last_value
        else:
            return self.last_value
	
