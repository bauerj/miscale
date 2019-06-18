import datetime

from lib.miscale import MiScalePoller

class MockDevice(object):
    def __init__(self, mac, sd):
        self.addr = mac
        self.sd = sd

    def getScanData(self):
        return self.sd


def test_parse_v2():
    mac = "00:00:00:00:00"
    dev_data = [(1, 'Flags', '06'), (2, 'Incomplete 16b Services', '0000181b-0000-1000-8000-00805f9b34fb'), (22, '16b Service Data', '1b1802a6e3070612142e111c02f839'), (9, 'Complete Local Name', 'MIBCS'), (255, 'Manufacturer', '5701ca2fff0f1861')]
    dev = MockDevice(mac, dev_data)
    p = MiScalePoller(mac)
    p.handleDiscovery(dev, True, True)
    assert p.weight == 74.2
    assert p.unit == "kg"
    assert p.weight_datetime == datetime.datetime(2019, 6, 18, 20, 46, 17)
    assert p.impedance == 540