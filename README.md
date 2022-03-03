PyController 
============

-----
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/orcephrye/PyController?include_prereleases)


A Game Pad key mapping utility for Linux. It works well with any modern USB device including Game Controllers 
(XBox One), Game Pads (Razer Tartarus), Keyboards and mice. 

* NOTE: It does not do macros IE: map one key press to multiple pre-programmed presses. This may be included in a future
release.
* NOTE: This app should run before any games run as it generates a new input device and some games cannot handle a new USB device being plugged in.


### Install

----
This utility requires Python 3.7+
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
```shell
lsusb | grep Razer
~> Bus 001 Device 006: ID 1532:0111 Razer USA, Ltd
```

If you do not see your listed device using the '--list-devices' flag for PyController but do see it under 'lsusb' then
it is possible there is a permissions issue. Checks perms like so:

```shell
ls -l /dev/input
crw-rw---- 1 root input 13,  64 Feb 26 12:47 event0

```

Most distros will automatically create the device with root:input permissions. You can add the user to the 'input' 
group like so: (you will need to be root to do this) You may also need to reboot after making this change.

```shell
sudo usermod -G input <username>
```

### Editing configuration

----
Upon running PyController for the first time this application should generate a PyController config file. This should be
located in "~/.config/PyController/". Run '--show-config-path' to verify:

```shell
python3 PyController.py --show-config-path

/home/rye/.config/PyController/main.yaml
```

Under the 'PyController/' config directory there will be a 'main.yaml' and two directories 'devices.d' and 'profiles.d'.

Edit the main.yaml to enable and disable logging. As well as to specify which device and profile config files should be
active. Example devices.yaml below:

```yaml
--- !Device # This has to be here it tells yaml to make the below information into a PyController Device object.
name: ExampleDevice # This has to be here to and with no spaces.
fullname: "Example Full Name of Device" # This is an optional key and used if there are multiple entries for the device
                                        # and there is a need to specify which device to capture. The full name can be 
                                        # seen using the flag '--list-devices'.
vendorid: '1111' # Also required and can be found via the lsusb command
productid: '2222' # Also required and can be found via the lsusb command
type: 'EV_KEY' # This should default to EV_KEY as it currently the only supported type. Others include EV_LED and so on.
keys: # This and all below it is not required. This is where you can remap keys.
  KEY_A: KEY_B # If you do want to remap a key it has to be the lines following the 'keys:' and it has spaced like this
    # example
  KEY_LEFTALT: KEY_SPACE
```

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

### Game Profiles 

----

PyController supports making key mapping specific to a game. It will run a monitor in another process which will watch 
for any configured game and then load the configured keymaps and unload those keymaps once the game is no longer
running. This also supports keymaps for specific devices per game. 

The example Yaml config file:

```yaml
# The 'executable' value should be the name or part of the full path of the application. Launch the game and use
#  'ps -wweo comm,args' to find what the game binary is called as it may not be what you expect.
RTS: # This will be the name of the profile
  executable: CompanyOfHeroes2 # This should be the name of the executable that runs your game. IE CompanyOfHeroes
  defualts-keys: # Below is a list of keys that should be remapped across all enabled devices
    KEY_LEFTALT: KEY_U # This must be spaced just like this. Invalid yaml entries will cause an error. Invalid KEY_* 
                       # entries will be ignored.
  devices:
    - Name: "Nostromo" # The name of the device as per the 'name' field in the device.yaml config file.
      keys:
        KEY_S: KEY_T
    - Name: "Tartarus_V2" # Can have more than one specified device.
      keys:
        KEY_S: KEY_T
RPGs: # There can be multiple profiles in the same config file.
  executable: [northgard, kingmaker.exe] # You can link multiple games to one profile. This is not case-sensitive
  keys:
    KEY_A: KEY_B
```

More information will follow.
