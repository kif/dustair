from machine import UART
import micropyGPS
from collections import namedtuple
Position = namedtuple("Position", ["Latitude", "Longitude" ])

class GPS:
    "A class receiving GPS data and serving the latest ones"
    def __init__(self, port=2, speed=9600, led=None):
        self.serial = UART(port, 9600)
        self.led = led
        self.gps = micropyGPS.MicropyGPS(1, "dd")
        self.buffer = bytearray(1024)
        self.cnt = 0
        # Implement a dummy semaphore
        self.busy = 0  # set to 1 on quick_update and 2 in update

    def __repr__(self):
        return "GPS object at %s" % self.get()

    @property
    def time(self):
        return self.gps.time

    @property
    def date(self):
        return "20" + self.gps.date_string("s_dmy").replace("/", "-")

    @property
    def position(self):
        lat = self.gps.latitude
        if lat[-1] == "S":
            lat = -lat[0]
        else:
            lat = lat[0]
        lon = self.gps.longitude
        if lon[-1] == "S":
            lon = -lon[0]
        else:
            lon = lon[0]
        return Position(lat, lon)

    def update(self):
        if self.busy:
            return
        else:
            self.busy = 2
        self.cnt += 1
        if self.serial.any():
            if self.led is not None:
                self.led.value(1)
            l = self.serial.readinto(self.buffer)
            start = None
            stop = None
            for i in range(l):
                if (start is None) and (self.buffer[i] == 36):  # $:
                    start = i
                    continue
                if (start is not None) and (self.buffer[i] == 10):  # \n
                    stop = i
            if (start is not None) and (stop is not None):
                try:
                    for i in range(start, stop + 1):
                        self.gps.update(chr(self.buffer[i]))
                except Exception as error:
                    print("Error %s on datagram\n %s" % (error, bytes(self.buffer[start:stop])))
                    raise error
            if self.led is not None:
                self.led.value(0)
        self.busy = 0

    def get(self, what=None):
        self.update()
        if what == "header":
            return "  Latitude  Longitude"
        elif what == "unit":
            return Position("degree", "degree")
        elif what == "text":
            position = self.position
            if position is not None:
                return "%10.6f %10.6f" % position
        else:
            return self.position
