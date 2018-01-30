import serial, pynmea2
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

