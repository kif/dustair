# Main program executed by micropython
from machine import UART, RTC
from esp32 import raw_temperature
import os
import uasyncio as asyncio
from sds import SDS
from collections import namedtuple
Time = namedtuple("Time", ["Hour", "Minute", "second" ])

uart_gps = UART(2, 9600)
uart_sds = UART(1, 9600)
sreader_gps = asyncio.StreamReader(uart_gps)  # Create a StreamReader
from gps import GPS
# gps = AS_GPS(sreader_gps, local_offset=1)  # Instantiate GPS
gps = GPS(sreader_gps, local_offset=1)
rtc = RTC()

def log(what):
    print("{4}:{5}:{6} ".format(*rtc.datetime()) + what)


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
    today = gps.date
    existing = len([1 for i in os.listdir() if i.startswith(today)])
    logfilename = "{}_{}.log".format(today, existing)
    return logfilename


def get_time(what=None):
    if what == "header":
        return "Time"
    elif what == "unit":
        return "HH:MM:SS"
    elif what == "text":
        return "{4}:{5}:{6}".format(*rtc.datetime())
    else:
        return rtc.datetime()[4:7]


async def disk_logger():
    base = get_logfilename()
    log("Saving in %s" % base)
    header = ["#started on {0}-{1}-{2} {4}:{5}:{6}".format(*rtc.datetime()),
              "#%8s %21s %13s %6s" % (get_time("header"), gps.get("header"), sds.get("header"), get_temprature("header")),
              ""]
    await asyncio.sleep(0)
    cnt = 0
    with open(base, "w") as logfile:
        logfile.write("\n".join(header))
        while True:
            data = "%12s %21s %13s %6s\n" % (get_time("text"), gps.get("text"), sds.get("text"), get_temprature("text"))
            logfile.write(data)
            cnt += 1
            if cnt % 60 == 0:
                log("Flush" + data[:-1])
                logfile.flush()
            await asyncio.sleep(1)

################################################################################
# MAIN
################################################################################
loop = asyncio.get_event_loop()
log("Waiting for GPS data")
loop.run_until_complete(gps.data_received(position=True, date=True))
print(rtc.datetime())
# Now only initialize the SDS
sreader_sds = asyncio.StreamReader(uart_sds)  # Create a StreamReader
sds = SDS(sreader_sds)  # Instantiate SDS
loop.run_until_complete(disk_logger())
