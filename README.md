# PyController
A Controller/Game Pad key mapping utility

This works with **Python 3.6+** using asyncio with the **evdev** library.

This tool was originally made for The Razor Nostromo but may work on other
game pads as well.

The main config file is called main.yaml. It references files for devices
in devices.d/. By default it looks for nostromo.yaml which exists.

To add your own device simply add the file in device.d following the
exampleDevice.yaml config file. Then reference that config file in
main.yaml.

A note about VendorID and ProductID. To find your device simply use the
command: # lsusb. The VendorID and ProductID will follow the word 'ID'
and be followed by the name of the device. They are separated by a colon
IE: ':'.

Example:

    ~> lsusb | grep Razer
    ~> Bus 001 Device 006: ID 1532:0111 Razer USA, Ltd


More information will follow.
