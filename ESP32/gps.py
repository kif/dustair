import time
from machine import UART
import micropyGPS
from collections import namedtuple
Position = namedtuple("Position", ["Latitude", "Longitude" ])

class GPS:
    "A class recieving GPS data and serving the latest ones"
    def __init__(self, port=2, speed=9600, led=None):
        self.serial = UART(port, 9600)
        self.led = led
        self.gps = micropyGPS.MicropyGPS(1, "dd")
        self.date = None
        self.time = None
        self.position = None
        self.buffer = bytearray(1024)
        # Implement a dymmy semaphore
        self.busy = 0  # set to 1 on quick_update and 2 in update

    def quick_update(self):
        if self.busy:
            return
        else:
            self.busy = 2

        if self.serial.any():
            if self.led is not None:
                self.led.value(1)
            l = self.serial.readinto(self.buffer)
            for i in range(l):
                self.gps.update(chr(self.buffer[i]))
            self.date = "20" + self.gps.date_string("s_dmy").replace("/", "-")
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

            self.position = Position(lat, lon)
            if self.led is not None:
                self.led.value(0)
        self.busy = 0

    def update(self, timeout=100):
        """Update data from GPS

        :param timeout: ms"""
        while self.busy:
            time.sleep_ms(10)
        self.busy = 1

        while not self.serial.any():
            time.sleep_ms(10)

        if self.led is not None:
            self.led.value(1)
        stream = b''

        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            stream += self.serial.readline()
        try:
            text = stream.decode("ascii")
        except UnicodeError as err:
            print(err)
            return
        for x in text:
            self.gps.update(x)

        self.date = "20" + self.gps.date_string("s_dmy").replace("/", "-")
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

        self.position = Position(lat, lon)
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
            if self.position:
                return "%10.6f %10.6f" % self.position
        else:
            return self.position
