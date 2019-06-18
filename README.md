# miscale
A library to receive and parse data from Xiaomi Body Composition Scale

## Usage

```python
from lib.miscale import MiScalePoller

# Your scale's MAC Address:
mac = "11:22:33:44:55"

poller = MiScalePoller(mac)
poller.update()
print(poller.weight, poller.unit, poller.weight_datetime, poller.impedance)
```
