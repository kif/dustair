try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

try:
    from micropython import const
except ImportError:
    const = lambda x : x

from collections import namedtuple
Dust = namedtuple("Dust", ["PM2_5", "PM10"])



# port=1, baud=9600
class SDS:
    "A class receiving particule measurement from SDS sensor"
    def __init__(self, sreader, callback=None):
        """
        :param sreader: async UART reader
        :param callback: to be called every update
        """
        self._sreader = sreader
        self._callback = callback
        self.last_value = None
        # Received status
        self._valid = 0  # Bitfield of received sentences
        if sreader is not None:  # Running with UART data
            loop = asyncio.get_event_loop()
            loop.create_task(self._run(loop))

    def __repr__(self):
        return "SDS sensor at {}".format(self.get())

    ##########################################
    # Data Stream Handler Functions
    ##########################################

    async def _run(self, loop):
        while True:
            res = await self._sreader.read()
            loop.create_task(self._update(res))
            await asyncio.sleep(0)  # Ensure task runs and res is copied

    async def _update(self, datagram):
        l = len(datagram)
        i = 0
        while i + 9 < l:
            b = datagram[i]
            c = datagram[i + 1]
            e = datagram[i + 9]
            if (b == 170) and (c == 192) and (e == 171):
                # likely a datagram
                data1, data2, data3, data4, data5, data6 = datagram[i + 2:i + 8]
                if (data1 + data2 + data3 + data4 + data5 + data6) % 256 == datagram[i + 8]:
                    # Yes it is a valid datagram
                    self.last_value = Dust((data1 + data2 * 256) / 10.0,
                                           (data3 + data4 * 256) / 10.0)
                    if callable(self._callback):
                        self._callback(self.last_value)
                    i += 10
                else:
                    i += 1
            await asyncio.sleep(0)

    def get(self, what=None):
        if what == "header":
            return " PM2.5   PM10"
        elif what == "unit":
            return "Dust", ["PM2.5 (µg/m³)", "PM10 (µg/m³)"]
        elif what == "text":
            value = self.last_value
            if value:
                return "{:6.1f} {:6.1f}".format(value[0], value[1])
        else:
            return self.last_value
