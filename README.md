PyController
============

-----
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/orcephrye/PyController?include_prereleases)

A Game Pad key mapping utility for Linux. 

This utility requires Python 3.7+

### Install

----
```sh
# Install requirements (pip should point to a Python 3.7+ environment.
pip install -r requirements.txt
```

This tool was originally made for The Razor Nostromo but can work on any other game pad that can be manipulated by
evdev. (Which should be all USB keyboard devices)

The main config file is called main.yaml. It references files for devices
in devices.d/. By default it looks for nostromo.yaml which exists.

### Finding and connecting devices

----

To add your own device simply add the file in device.d following the
exampleDevice.yaml config file. Then reference that config file in
main.yaml.

A note about VendorID and ProductID. To find your device simply use the
command: 

```sh
python3 PyController.py --list-devices
```

You can also use the 'lsusb' command. The VendorID and ProductID will follow the word 'ID'
and be followed by the name of the device. They are separated by a colon
IE: ':'.

Example:
```sh
lsusb | grep Razer
~> Bus 001 Device 006: ID 1532:0111 Razer USA, Ltd
```

If you do not see your listed device using the '--list-devices' flag for PyController but do see it under 'lsusb' then
it is possible there is a permissions issue. Checks perms like so:

```sh
ls -l /dev/input
crw-rw---- 1 root input 13,  64 Feb 26 12:47 event0

```

Most distros will automatically create the device with root:input permissions. You can add the user to the 'input' 
group like so: (you will need to be root to do this)

```shell
sudo usermod -G input <username>
```

### Editing configuration

----
You can find examples of config files in the 'device.d' folder. 

```yaml
--- !Device # This has to be here it tells yaml to make the below information into a PyController Device object.
name: ExampleDevice # This has to be here to and with no spaces.
vendorid: '1111' # Also required and can be found via the lsusb command
productid: '2222' # Also required and can be found via the lsusb command
type: 'EV_KEY' # This should default to EV_KEY as it currently the only supported type. Others include EV_LED and so on.
keys: # This and all below it is not required. This is where you can remap keys.
  KEY_A: KEY_B # If you do want to remap a key it has to be the lines following the 'keys:' and it has spaced like this example
  KEY_LEFTALT: KEY_SPACE
```

You will need to specify which configs to use in the main.yaml config file. 

Too determine what KEYS to use you can use the following flags:

```sh 
# Lists a printout of keys on a standard QWERTY keyboard
python3 PyController.py --print-classic-keys
# Provides the specified device's aviable key presses.
python3 PyController.py --print-capabilities XXXX:XXXX
# If you are still having trouble using this flag will listen to the device. 
# You can try different keys to see what there symbol is.
python3 PyController.py --print-key-presses XXXX:XXXX
```


More information will follow.
