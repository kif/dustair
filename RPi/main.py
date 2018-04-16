#!/home/jerome/py3/bin/python3

"Simple logger"

DISK = "/mnt/dust"

import sys
import os
import logging
import threading
import signal
import time
import datetime
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

from sds import SDS
from gps import GPS
from dht import DHT

quit_event = threading.Event()

sds = SDS(quit_event=quit_event)
gps = GPS(quit_event=quit_event)
dht = DHT(quit_event=quit_event)

def signal_handler(sig, frame):
    logger.warning("Ctrl-C pressed, quitting")
    quit_event.set()
    sys.exit(0)

def mount_disk():
    if not os.path.ismount(DISK):
        os.system("mount %s"%dist)

if __name__ == "__main__":
    #Start all acquisition threads
    gps.start()
    sds.start()
    dht.start()
    mount_disk()
    while gps.date is None:
        logger.warning("Waiting for GPS for date")
        time.sleep(1.0)
        
    today = gps.date.strftime("%Y-%m-%d")
    existing = len([1 for i in os.listdir(DISK) if i.startswith(today)])
    base = os.path.join(DISK, today+"_%s.log"%existing)
    logger.info("Saving in %s"%base)
    cnt = 0
    now = datetime.datetime(gps.date.year,gps.date.month, gps.date.day, 
                            gps.time.hour, gps.time.minute, gps.time.second)
    header = ["#started on %s UTC"%now.strftime("%c"),
              "#%8s %21s %13s %20s"%("Time", gps.get("header"), sds.get("header"), dht.get("header")),
              ""]
    
    with open(base, "w") as logfile:
        logfile.write(os.linesep.join(header))
        while not quit_event.is_set():
            try:
                data = "%8s %21s %13s %20s"%(gps.time.isoformat(), gps.get("text"), sds.get("text"), dht.get("text"))
                logger.info(data)
                logfile.write(data+os.linesep)
                cnt+=1
                if cnt%60==0:
                    logger.info("flush")
                    logfile.flush()
                time.sleep(1.)
            except KeyboardInterrupt:
                logger.info("Gracefully exiting")
                quit_event.set()
        
    
