#!/usr/bin/env python
from pyftdi.ftdi import Ftdi

ft232h_pid = Ftdi.PRODUCT_IDS[Ftdi.FTDI_VENDOR]["ft232h"]
id_tuple = (Ftdi.FTDI_VENDOR, ft232h_pid)

devices = Ftdi.find_all([id_tuple])
if devices:
    for device in devices:
        print(device)
else:
    print("No FT232H devices found.")
