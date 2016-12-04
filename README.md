# PyController
A Game Pad key mapping utility

This utility works only on Python 2.7 and uses evdev and PyYAML.
# pip2.7 install evdev
# pip2.7 install PyYAML

This tool was originally made for The Razor Nostromo but may work on other
game pads as well.

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
~> lsusb | grep Razer
Bus 001 Device 006: ID 1532:0111 Razer USA, Ltd
~>

More information will follow.
