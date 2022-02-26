PyController
============

-----
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)

A Game Pad key mapping utility for Linux. 

This utility requires Python 3.6+

```sh
# Install requirements (pip should point to a Python 3.6+ environment.
pip install -r requirements.txt
```

This tool was originally made for The Razor Nostromo but can work on any other game pad that can be manipulated by
evdev. (Which should be all USB keyboard devices)

The main config file is called main.yaml. It references files for devices
in devices.d/. By default it looks for nostromo.yaml which exists.

To add your own device simply add the file in device.d following the
exampleDevice.yaml config file. Then referance that config file in
main.yaml.

A note about VendorID and ProductID. To find your device simply use the
command: # lsusb. The VendorID and ProductID will follow the word 'ID'
and be followed by the name of the device. They are seperated by a colon
IE: ':'.

Example:
```sh
lsusb | grep Razer
~> Bus 001 Device 006: ID 1532:0111 Razer USA, Ltd
```

More information will follow.
