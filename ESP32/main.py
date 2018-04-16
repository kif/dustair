# Main program executed by micropython

import os, time
from machine import Timer, Pin
from gps import GPS, NO_POSITION
from sds import SDS

led = Pin(16, Pin.OUT)
led.value(0)
gps = GPS(2, 9600)
sds = SDS(1)
poll_delay = 200  # ms

def update_all(*arg, **kwarg):
    led.value(1)
    sds.quick_update()
    gps.quick_update()
    led.value(0)

sds.update()
gps.update()
update_all()

# try:
#     timer = Timer(-1)
#     timer.init(period=1000,  # every second
#                mode=Timer.PERIODIC,
#                callback=update_all)
# except OSError:
#     pass

def wait_data():
    print("Wait for data to come from the GPS and from the SDS")
    sync = (sds.last_value is not None) and (gps.position != NO_POSITION) and (gps.date != "2000-00-00")
    while not sync:
        time.sleep_ms(poll_delay)
        update_all()
        print(sds.last_value, gps.position, gps.date)
        sync = (sds.last_value is not None) and (gps.position != NO_POSITION) and (gps.date != "2000-00-00")
    print("GPS and SDS initialized")


def main():
    linesep = "\n"
    today = gps.date
    existing = len([1 for i in os.listdir() if i.startswith(today)])
    base = "%s_%s.log" % (today, existing)
    print("Saving in %s" % base)
    cnt = 0
    header = ["#started on %s UTC" % gps.time,
              "#%8s %21s %13s" % ("Time", gps.get("header"), sds.get("header")),
              ""]

    with open(base, "w") as logfile:
        logfile.write(linesep.join(header))
        quit = False
        now = time.ticks_ms()
        update_all()
        while not quit:
            try:
                data = "%12s %21s %13s\n" % (gps.time, gps.get("text"), sds.get("text"))
                last = time.ticks_ms()
                print(data[:-1])
                logfile.write(data + linesep)
                cnt += 1
                if cnt % 60 == 0:
                    print("Flush")
                    logfile.flush()
                while time.ticks_diff(time.ticks_ms(), last) < 1000:
                    gps.quick_update()
                    # 200ms -> 700 bytes, fits in the buffer !
                    time.sleep_ms(poll_delay)
                # update_all()
            except KeyboardInterrupt:
                print("Gracefully exiting")
                quit = True

wait_data()
main()
