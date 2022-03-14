#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description: This package holds the Device class which keeps information about a particular device.


import logging
import yaml
import evdev
import traceback
import time
from evdev import InputDevice, UInput, InputEvent, categorize, ecodes as e
from PyController.ArgumentWrapper import CLASSIC_KEYBOARD, CONTROLLER_BUTTONS


log = logging.getLogger('Devices')


async def async_device_worker(device):
    """
        This is what listens for new inputs and routes them to a virtual device possibly changed if it has a key map.
    """
    # All methods are specified ahead of time to help with optimization
    async_read_loop = device.evdevice.async_read_loop
    mapEvent = device.keymapper.map_event
    write_event = device.outDevice.write_event
    syn = device.outDevice.syn
    try:
        async for ev in async_read_loop():
            write_event(mapEvent(ev, device))
            syn()
    except Exception as e:
        log.error(f'An Exception occurred on Device: {device.name}\n{e}\n')
        log.debug(f'traceback for exception: {e}\n{traceback.format_exc()}')


class Device(yaml.YAMLObject):
    """
        This is a class designed to hold the information regarding a particular device. It is loaded in via a yaml
        config file located inside 'devices.d'. The file will need to contain 'vendorid', 'productid', 'name' sand type.
        Keys are optional and is supposed to be a dictionary. 'fullname' is optional and is meant to deal with devices
        that has multiple input devices.
    """
    yaml_tag = u'!Device'

    vendorid = None
    productid = None
    name = None
    fullname = None
    keys = None
    type = None
    keymapper = None
    deviceKeyMap = None

    evdevice = None
    outDevice = None

    def __init__(self, vendorid, productid, name, type=None, keys=None, fullname=None):
        """
            This is not used by yaml when creating the Device object. Do not edit this to troubleshoot unless you
            intend to 'manually' create a Device class.
        :param vendorid: int - Find this out via lsusb or '--list-devices' flag.
        :param productid: int - Find this out via lsusb or '--list-devices' flag.
        :param name: str - The name of the Device object. This will be used to match against for profile.d configs.
        :param type: str - Either EV_KEY or EV_BUTTON Almost certainly EV_KEY.
        :param keys: dict - Example: {'KEY_A': 'KEY_B'}
        :param fullname: str - Used to avoid confusion when a device appears multiple times in lsusb or '--list-devices'
        """
        self.vendorid = str(vendorid)
        self.productid = str(productid)
        self.name = name
        self.fullname = fullname
        self.type = type
        self.evdevice = None
        if keys is None:
            self.keys = {}
        else:
            self.keys = keys

    def __str__(self):
        return f"{getattr(self.evdevice, 'name', '')} - {getattr(self.evdevice, 'path', '')}"

    def __hash__(self):
        return hash(self.name)

    def setup(self, keymapper, inputDevices):
        """
            Used by the DeviceManager. This checks things and finishes setting up the Device with the necessary
        :param keymapper: KeyMapper object
        :param inputDevices: List of InputDevices from evdev.
        :return: None
        """
        self.check_device_variables()
        self.find_device(inputDevices)
        if self.isValid:    # Continue if 'findDevice' found the input devices on the OS.
            self.set_key_mapper(keymapper)
            self.generate_ouput_device()

    def set_key_mapper(self, keymapper):
        """
            This sets the keymapper and gets back a dictionary of mapped keys
        :param keymapper: KeyMapper class object
        :return: None
        """
        self.keymapper = keymapper
        self.deviceKeyMap = self.keymapper.add_device_keymap(self, self.keys)

    def check_device_variables(self):
        """
            This is called by the DeviceManager class. It is used because the '__init__' magic method for Device isn't
            used by yaml when creating these classes. So a secondary check of the variables is necessary to help prevent
            a problem.
        :return:
        """
        self.vendorid = str(self.vendorid)
        self.productid = str(self.productid)
        self.name = str(self.name)
        if isinstance(self.type, str):
            self.type = self.type.lower()
            if self.type not in ['EV_KEY', 'EV_BUTTON']:
                self.type = 'EV_KEY'
        else:
            self.type = 'EV_KEY'
        if not isinstance(self.keys, dict):
            self.keys = {}
        self.evdevice = None

    def find_device(self, deviceList):
        """
            This is called by the DeviceManager class. The Device tries to find the associated 'input' IO files on the
            OS that are linked to the device in question. It compares the vendorid and productid which both have to
            match. There are devices that create multiple inputs. This links them together.
        :param deviceList:
        :return:
        """
        self.evdevice = None
        for dev in deviceList:
            if self.vendorid in Device._to_hex(dev.info.vendor) and self.productid in Device._to_hex(dev.info.product):
                log.info(f'Found device {dev}.')
                if self.type == self.get_device_type(dev):
                    if self.fullname is not None and self.fullname != dev.name:
                        continue
                    if self.evdevice is not None:
                        log.error(f"Device {self.name} was found more then once! This can be caused by error in "
                                  f"configuration. Suggestion is to use the 'fullname' key in the device's yaml "
                                  f"config file. ")
                        raise Exception("This device was found more then once!")
                    self.evdevice = dev
        if self.evdevice is None:
            log.error(f"Device {self.name} not found!")
        return self.evdevice

    def map_event(self, event):
        """
            This is called upon by the DeviceInputWorker associated with this Device. The job is to check to see if the
            event sent (key pressed) is associated with a map.
        :param event: InputEvent object
        :return: InputEvent object
        """
        return self.keymapper.map_event(event, self)

    def grab(self):
        """
            Once this is called the device will no longer be readable by any other program. It will be up to this
            program to relay whatever events onward.
        :return:
        """
        log.info("Grabbing input devices associated with: %s" % self.name)
        if self.evdevice:
            self.evdevice.grab()

    def ungrab(self):
        """
            This happens when the program is ready to shut down. It releases the grab so that other programs and once
            again read this device
        :return:
        """
        log.info("Releasing input devices associated with: %s" % self.name)
        if self.evdevice:
            self.evdevice.ungrab()

    def close(self):
        """
            The 'generateOutputDevice' method creates a UInput device object based on these devices capabilities. This
            method deletes that device.
        :return:
        """
        if self.outDevice:
            log.info("Closing output devices associated with: %s" % self.name)
            self.outDevice.syn()
            self.outDevice.close()

    def generate_ouput_device(self):
        """
            This creates a new Output device on the OS that takes on the capabilities of the input devices associated
            with this device.
        :return:
        """
        caps = self.evdevice.capabilities()
        newCaps = {e.EV_KEY: caps.get(e.EV_KEY, [])}
        # Gets the keys for a classic keyboard and combines them with existing keys of the device.
        newCaps[1] = list(set(newCaps.get(1)).union(set([getattr(e, key)
                                                         for key in CLASSIC_KEYBOARD + CONTROLLER_BUTTONS
                                                         if hasattr(e, key)])))

        # self.outDevice = UInput.from_device(self.evdevice, name=self.name + '_output')
        self.outDevice = UInput(newCaps, name=self.name+'_output')

    def inject_input(self, type='EV_KEY', key='KEY_Q'):
        self.evdevice.write_event(InputEvent(time.time(),
                                             0,
                                             getattr(e, type, 'EV_KEY'),
                                             getattr(e, key, 'KEY_Q'),
                                             1))
        self.evdevice.write_event(InputEvent(time.time(),
                                             1,
                                             getattr(e, type, 'EV_KEY'),
                                             getattr(e, key, 'KEY_Q'),
                                             0))

    def read_input(self):
        """
            This is used for testing the devices key presses
        """
        for event in self.evdevice.read_loop():
            if event.type == e.EV_KEY:
                yield categorize(event)

    @property
    def isValid(self) -> bool:
        return self.evdevice is not None

    @staticmethod
    def is_keyboard(device):
        return len(device.capabilities().get(1, [])) > 160

    @staticmethod
    def has_keys(device):
        return len(device.capabilities().get(1, [])) > 0

    @staticmethod
    def is_mouse(device):
        return len(device.capabilities().get(2, [])) > 1

    @staticmethod
    def get_device_type(device):
        if Device.is_keyboard(device) and Device.is_mouse(device):
            return 'both'
        elif Device.is_mouse(device):
            return 'EV_BUTTON'
        elif Device.is_keyboard(device) or Device.has_keys(device):
            return 'EV_KEY'
        return 'both'

    @staticmethod
    def _to_hex(hexString, standardLength=4):
        """
            This is a little short helper method that reformat the hex to match that which is found in the yaml config
            file.
        :param hexString:
        :param standardLength:
        :return:
        """
        return hex(hexString)[2:].rjust(standardLength, '0')


class DeviceManager(object):
    """
        This classes acts like an interface of sorts to the different devices. The idea is that this code can handle
        multiple devices so the PyController class needs easy access to all those devices. This class manages them.
    """

    settings = None
    inputDevices = None
    keymapper = None
    devices = None

    def __init__(self, settingsManager, keymapper):
        """
            This requires both the SettingsManager and KeyMapper classes. It will use the SettingsManager to load all
            the different devicename.yaml config files enabled in the main.yaml. Each one should load a new Device
            class. It will pass the KeyMapper along to the different devices it finds.
            NOTE: the 'inputDevices' variable that is set actually is a list of all known input devices on the box. Each
                device will look through that list to try to find its device. This is a large point of failure.
        :param settingsManager: SettingsManager object
        :param keymapper: KeyMapper object
        """
        self.settings = settingsManager
        self.keymapper = keymapper
        self.inputDevices = [InputDevice(fn) for fn in evdev.list_devices()]
        self.get_device_configs()

    def __str__(self):
        return '\n'.join([f"{dev.path} - {dev.name} - {Device._to_hex(dev.info.vendor)}:"
                          f"{Device._to_hex(dev.info.product)}"
                          for dev in self.inputDevices])

    def get_device_configs(self):
        """
            This uses the SettingsManager protected variable 'devices' to grab the list of yaml config files from the
            main.yaml config file. It will run the 'load_yaml' method from SettingsManager with the parameter
            'device=True' for each yaml config file it sees. It will then iterate through the nearly created list of
            devices and run a series of methods on them setting them up.
        :return:
        """
        self.devices = []
        for device in self.settings.devices:
            self.devices.append(self.settings.load_yaml(device, device=True))
        for device in self.devices:
            device.setup(self.keymapper, self.inputDevices)
        return self.devices

    def find_devices(self):
        for device in self.devices:
            device.find_device(self.inputDevices)

    def grab_devices(self):
        log.info("Grabbing all configured devices")
        for device in self.devices:
            device.grab()

    def ungrab_devices(self):
        log.info("Releasing all configured devices")
        for device in self.devices:
            device.ungrab()

    def close_devices(self):
        log.info("Closing all evdev UInput devices")
        for device in self.devices:
            device.close()
        while len(self.devices) > 0:
            item = self.devices.pop()
            del item

    def delete_inputs(self):
        log.info("Deleting all Input Devices")
        for item in self.inputDevices:
            item.close()
        while len(self.inputDevices) > 0:
            item = self.inputDevices.pop()
            del item
