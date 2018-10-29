# Main program executed by micropython

import os
import uasyncio as asyncio

from machine import UART, RTC
from esp32 import raw_temperature
from sds import SDS
from as_GPS import AS_GPS
from collections import namedtuple
Position = namedtuple("Position", ["Latitude", "Longitude" ])
Time = namedtuple("Time", ["Hour", "Minute", "second" ])

uart_gps = UART(2, 9600)
uart_sds = UART(1, 9600)
sreader_gps = asyncio.StreamReader(uart_gps)  # Create a StreamReader
sreader_sds = asyncio.StreamReader(uart_sds)  # Create a StreamReader
from gps import GPS
# gps = AS_GPS(sreader_gps, local_offset=1)  # Instantiate GPS
gps = GPS(sreader_gps, local_offset=1, callback=print)
sds = SDS(sreader_sds)  # Instantiate SDS
rtc = RTC()

def log(what):
    print("{4}:{5}:{6} ".format(*rtc.datetime()) + what)

def init_rtc():
    date = gps.date
    y = date[2] + 2000
    m = date[1]
    d = date[0]
    wod = gps._week_day(y, m, d)
    rtc.datetime((y, m, d, wod) + gps.local_time + (0,))


def get_temprature(what=None):
    if what == "header":
        return " Temp."
    elif what == "unit":
        return "degreeC"
    elif what == "text":
        C = (raw_temperature() - 32) / 1.8
        return "%5.2f" % C
    else:
        C = (raw_temperature() - 32) / 1.8


def get_logfilename():
    today = "20{2}-{1}-{0}".format(*gps.date)
    existing = len([1 for i in os.listdir() if i.startswith(today)])
    logfilename = "{}_{}.log".format(today, existing)
    return logfilename

def get_gps(what=None):
    if what == "header":
        return "  Latitude  Longitude"
    elif what == "unit":
        return Position("degree", "degree")
    elif what == "text":
        return "%10.6f %10.6f" % (gps.latitude()[0], gps.longitude()[0])
    else:
        return Position(gps.latitude()[0], gps.longitude()[0])

def get_time(what=None):
    if what == "header":
        return "Time"
    elif what == "unit":
        return "HH:MM:SS"
    elif what == "text":
        return "{4}:{5}:{6}".format(*rtc.datetime())
    else:
        return rtc.datetime()[4:7]

async def gps_synchro():
    await gps.data_received(position=True)


async def disk_logger():
    base = get_logfilename()
    log("Saving in %s" % base)
    header = ["#started on {0}-{1}-{2} {4}:{5}:{6}".format(*rtc.datetime()),
              "#%8s %21s %13s %6s" % (get_time("header"), get_gps("header"), sds.get("header"), get_temprature("header")),
              ""]
    await asyncio.sleep(0)
    cnt = 0
    with open(base, "w") as logfile:
        logfile.write("\n".join(header))
        while True:
            data = "%12s %21s %13s %6s\n" % (get_time("text"), get_gps("text"), sds.get("text"), get_temprature("text"))
            logfile.write(data)
            cnt += 1
            if cnt % 60 == 0:
                log("Flush" + data[:-1])
                logfile.flush()
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
log("Waiting for GPS data")
loop.run_until_complete(gps_synchro())
init_rtc()
loop.run_until_complete(disk_logger())
