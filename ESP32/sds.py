import time
from machine import UART
from collections import namedtuple
Dust = namedtuple("Dust", ["PM2_5", "PM10"])

class SDS:
    "A class receiving particule measurement from SDS sensor"
    def __init__(self, port=1, buffer_size=1024):

        self.serial = UART(port, 9600)
        self.buffer_size = buffer_size
        self.buffer = bytearray(self.buffer_size)
        self.cnt = 0
        # Implement a dummy lock
        self.busy = 0  # set to lock
        self.last_value = None

    def __repr__(self):
        return "SDS sensor at %s" % self.get()

    def parse_datagram(self, start, end):
        for i in range(start, end - 9):
            b = self.buffer[i]
            c = self.buffer[i + 1]
            e = self.buffer[i + 9]
            if (b == 170) and (c == 192) and (e == 171):
                # likely a datagram
                data1, data2, data3, data4, data5, data6 = self.buffer[i + 2:i + 8]
                if (data1 + data2 + data3 + data4 + data5 + data6) % 256 == self.buffer[i + 8]:
                    # Yes it is a valid datagram
                    self.last_value = Dust((data1 + data2 * 256) / 10.0,
                                           (data3 + data4 * 256) / 10.0)
                    return i + 10
#                 else:
#                     print("SDS: checksum error")
#             else:
#                 print("SDS: no data found in %s" % (bytes(self.buffer[start:end])))
        return end - 9

    def quick_update(self):
        if self.busy:
            return
        else:
            self.busy = 2
        self.cnt += 1
        if self.serial.any():
            l = self.serial.readinto(self.buffer)
            start = 0
            while start <= l - 10:
                start = self.parse_datagram(start, l)
        self.busy = 0

    def update(self, timeout=10000, verbose=True):
        start = time.ticks_ms()
        while not self.serial.any():
            if time.ticks_diff(time.ticks_ms(), start) > timeout:
                if verbose:
                    print("SDS: timeout")
                break
            else:
                time.sleep_ms(10)
        else:
            self.quick_update()
            if verbose:
                print("SDS updated")

    def get(self, what=None):
        self.quick_update()
        if what == "header":
            return " PM2.5   PM10"
        elif what == "unit":
            return "Dust", ["PM2.5 (µg/m³)", "PM10 (µg/m³)"]
        elif what == "text":
            value = self.last_value
            if value:
                return "%6.1f %6.1f" % (value[0], value[1])
        else:
            return self.last_value
