""""
Read data from Mi Smart Scale (v1 and v2).
"""

from datetime import datetime, timedelta
import logging
from bluepy import btle

MI_SCALE_V1 = '1d18'
MI_SCALE_V2 = '1b18'

_LOGGER = logging.getLogger(__name__)



class InvalidWeightUnitException(Exception):
    pass


class MiScalePoller(object):
    """"
    A class to read data from Mi Temp plant sensors.
    """

    def __init__(self, mac, scan_timeout=5.0):
        """
        Initialize a Mi Scale Poller for the given MAC address.
        """

        self._mac = mac
        self.scanner = btle.Scanner().withDelegate(self)
        self.scan_timeout = scan_timeout

        self.weight = None
        self.unit = None
        self.weight_datetime = None
        self.impedance = None

    def update(self):
        self.scanner.scan(self.scan_timeout)

    # noinspection PyPep8Naming
    def handleDiscovery(self, dev, is_new_dev, is_new_data):
        if dev.addr != self._mac or not is_new_dev:
            return
        for (ad_type, desc, data) in dev.getScanData():
            if ad_type == 22:
                unit_type = data[4:6]
                if data.startswith(MI_SCALE_V1):
                    weight = int((data[8:10] + data[6:8]), 16) * 0.01

                    if unit_type in ('03', 'b3'):
                        unit = 'lbs'
                    elif unit_type in ('12', 'b2'):
                        unit = 'jin'
                    elif unit_type in ('22', 'a2'):
                        unit = 'kg'
                        weight /= 2
                    else:
                        raise InvalidWeightUnitException("Invalid unit from Mi Scale: {}".format(data[4:6]))
                        continue

                    self.weight = weight
                    self.unit = unit

                if data.startswith(MI_SCALE_V2):
                    weight = int((data[28:30] + data[26:28]), 16) * 0.01

                    if unit_type == "03":
                        unit = 'lbs'
                    elif unit_type == '02':
                        unit = 'kg'
                        weight /= 2
                    else:
                        raise InvalidWeightUnitException("Invalid unit from Mi Scale: {}".format(data[4:6]))
                        continue

                    self.weight = weight
                    self.unit = unit

                    self.weight_datetime = datetime.strptime(
                        str(int((data[10:12] + data[8:10]), 16)) + " " + str(int((data[12:14]), 16)) + " " + str(
                            int((data[14:16]), 16)) + " " + str(int((data[16:18]), 16)) + " " + str(
                            int((data[18:20]), 16)) + " " + str(int((data[20:22]), 16)), "%Y %m %d %H %M %S")
                    self.impedance = int((data[24:26] + data[22:24]), 16)

