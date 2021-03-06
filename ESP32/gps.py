import utime
from machine import RTC
from collections import namedtuple
Position = namedtuple("Position", ["Latitude", "Longitude" ])
try:
    from micropython import const
except ImportError:
    const = lambda x : x

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio
from math import modf
NO_POSITION = Position(0.0, 0.0)

DOLLAR = const(36)
STAR = const(42)
BACKR = const(13)
BACKN = const(10)

# Sentence types
RMC = const(1)
GLL = const(2)
VTG = const(4)
GGA = const(8)
GSA = const(16)
GSV = const(32)
# Messages carrying data
POSITION = const(RMC | GLL | GGA)
ALTITUDE = const(GGA)
DATE = const(RMC)
COURSE = const(RMC | VTG)


def timed_function(f, *args, **kwargs):
    myname = str(f).split()[1]
    def new_func(*args, **kwargs):
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta / 1000))
        return result
    return new_func


class GPS:
    "A class receiving GPS data and serving the latest ones"
    def __init__(self, sreader, local_offset=0, callback=None):
        self._sreader = sreader  # If None testing: update is called with simulated data
        self._callback = callback
        self._local_offset = local_offset
        self.cnt = 0
        self._rtc = RTC()
        self._latitude = None
        self._longitude = None
        self._altitude = None
        self._time_fixed = False
        # Key: currently supported NMEA sentences. Value: parse method.
        self.supported_sentences = {b'GPRMC': self._gprmc, b'GLRMC': self._gprmc, b'GNRMC': self._gprmc,
                                    b'GPGGA': self._gpgga, b'GLGGA': self._gpgga, b'GNGGA': self._gpgga,
                                    b'GPGLL': self._gpgll, b'GLGLL': self._gpgll, b'GNGLL': self._gpgll,
                                    }
        # Received status
        self._valid = 0  # Bitfield of received sentences
        if sreader is not None:  # Running with UART data
            loop = asyncio.get_event_loop()
            loop.create_task(self._run(loop))

    def __repr__(self):
        return "GPS object at {}".format(self.get())

    @property
    def time(self):
        if not self._time_fixed:
            print("warning: time not fixed")
        now = self._rtc.datetime()
        return "{4:02d}:{5:02d}:{6:02d}.{7:06d}".format(*now)

    @property
    def date(self):
        if not self._time_fixed:
            print("warning: time not fixed")
        now = self._rtc.datetime()
        return "{0:04d}-{1:02d}-{2:02d}".format(*now)

    @property
    def datetime(self):
        if not self._time_fixed:
            print("warning: time not fixed")
        return self._rtc.datetime()

    @property
    def position(self):
        return Position(self._latitude, self._longitude)

    ##########################################
    # Data Stream Handler Functions
    ##########################################

    async def _run(self, loop):
        while True:
            raw = await self._sreader.readline()

            loop.create_task(self._update(raw))
            await asyncio.sleep(0)  # Ensure task runs and res is copied

    # Update takes a line of text
    async def _update(self, line):
        if self.check_crc(line):
            self.cnt += 1
        else:
            await asyncio.sleep(0)
            return
        sentence = line.split(b"*")[0].split(b",")
        data_type = sentence[0][1:]
        if data_type in self.supported_sentences:
            try:
                s_type = self.supported_sentences[data_type](sentence)  # Parse
            except ValueError:
                s_type = False
            await asyncio.sleep(0)
            if s_type and callable(self._callback):
                self._callback(data_type.decode("utf-8"))

    # Data Validity. On STARtup data may be invalid. During an outage it will be absent.
    async def data_received(self, position=False, date=False):
        self._valid = 0  # Assume no messages at start
        result = False
        while not result:
            result = True
            await asyncio.sleep(1)  # Successfully parsed messages set ._valid bits
            if position and not self._valid & POSITION:
                result = False
            if date and not self._valid & DATE:
                result = False
            # After a hard reset the chip sends course messages even though no fix
            # was received. Ignore this garbage until a fix is received.

    # 8-bit xor of characters between "$" and "*". Takes 6ms on Pyboard!
    @staticmethod
    def check_crc(line):
        crc_xor = None
        start = False
        for i, c in enumerate(line):
            if c == DOLLAR:
                start = True
                crc_xor = 0
                continue
            if c == STAR:
                start = False
                break
            if start:
                crc_xor ^= c
        ascii_crc = ""
        for c in line[i + 1:]:
            if c == BACKR:
                break
            else:
                ascii_crc += chr(c)
        try:
            crc = int(ascii_crc, 16)
        except ValueError:
            return False
        return crc_xor == crc

    def get(self, what=None):
        if what == "header":
            return "  Latitude  Longitude"
        elif what == "unit":
            return Position("degree", "degree")
        elif what == "text":
            position = self.position
            if position is not None:
                return "{0:10.6f} {1:10.6f}".format(*position)
        else:
            return self.position

    # Some internal methods for parsing the string of interest
    def _gpgll(self, gps_segments):  # Parse GLL sentence
        # Check Receiver Data Valid Flag
        if len(gps_segments) <= 7:
            raise ValueError
        if gps_segments[6] != b'A':  # Invalid. Don't update data
            raise ValueError

        # Data from Receiver is Valid/Has Fix. Longitude / Latitude
        self._fix(gps_segments, 1, 3)
        # Update Last Fix Time
        self._valid |= GLL
        return GLL

    # Chip sends rubbish RMC messages before first PPS pulse, but these have
    # data valid set to 'V' (void)
    def _gprmc(self, gps_segments):  # Parse RMC sentence
        # UTC Timestamp and date. Can raise ValueError.
        self._set_date_time(gps_segments[1], gps_segments[9])
        # Check Receiver Data Valid Flag ('A' active)
        if gps_segments[2] != b'A':
            raise ValueError

        # Data from Receiver is Valid/Has Fix. Longitude / Latitude
        # Can raise ValueError.
        self._fix(gps_segments, 3, 5)
        self._valid |= RMC
        return RMC

    def _gpgga(self, gps_segments):  # Parse GGA sentence
        # Get Fix Status
        fix_stat = int(gps_segments[6])

        # Process Location and Altitude if Fix is GOOD
        if fix_stat:
            # Longitude / Latitude
            self._fix(gps_segments, 2, 4)
            # Altitude / Height Above Geoid
            altitude = float(gps_segments[9])
            # Update Object Data
            self._altitude = altitude
            self._valid |= GGA
        return GGA

    # Caller traps ValueError
    def _fix(self, gps_segments, idx_lat, idx_long):
        # Latitude
        l_string = gps_segments[idx_lat]
        lat_degs = int(l_string[0:2]) + float(l_string[2:]) / 60.0
        lat_hemi = gps_segments[idx_lat + 1]
        # Longitude
        l_string = gps_segments[idx_long]
        lon_degs = int(l_string[0:3]) + float(l_string[3:]) / 60.0
        lon_hemi = gps_segments[idx_long + 1]

        if lat_hemi not in b'NS'or lon_hemi not in b'EW':
            raise ValueError

        self._latitude = lat_degs if lat_hemi == b"N" else -lat_degs
        self._longitude = lon_degs if lon_hemi == b"E" else -lon_degs

    def _set_date_time(self, utc_string, date_string):
        if not date_string or not utc_string:
            raise ValueError
        if not self._time_fixed:
            hrs = int(utc_string[0:2]) + self._local_offset  # h
            mins = int(utc_string[2:4])  # mins
            # Secs from MTK3339 chip is a float but others may return only 2 chars
            # for integer secs. If a float keep epoch as integer seconds and store
            # the fractional part as integer ms (ms since midnight fits 32 bits).
            fss, fsecs = modf(float(utc_string[4:]))
            secs = int(fsecs)
            usecs = int(fss * 1000000)
            d = int(date_string[0:2])  # day
            m = int(date_string[2:4])  # month
            y = int(date_string[4:6]) + 2000  # year
            wday = self._week_day(y, m, d)
            self._rtc.datetime((y, m, d, wday, hrs, mins, secs, usecs))
            self._time_fixed = True

    # Return day of week from date. Pyboard RTC format: 1-7 for Monday through Sunday.
    # https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date-in-python?noredirect=1&lq=1
    # Adapted for Python 3 and Pyboard RTC format.
    @staticmethod
    def _week_day(year, month, day, offset=[0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]):
        aux = year - 1700 - (1 if month <= 2 else 0)
        # day_of_week for 1700/1/1 = 5, Friday
        day_of_week = 5
        # partial sum of days betweem current date and 1700/1/1
        day_of_week += (aux + (1 if month <= 2 else 0)) * 365
        # leap year correction
        day_of_week += aux // 4 - aux // 100 + (aux + 100) // 400
        # sum monthly and day offsets
        day_of_week += offset[month - 1] + (day - 1)
        day_of_week %= 7
        day_of_week = day_of_week if day_of_week else 7
        return day_of_week