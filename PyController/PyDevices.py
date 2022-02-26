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


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('Devices')


async def AsyncDeviceWorker(device):
    try:
        async for ev in device.evdevice.async_read_loop():
            for e in device.keymapper.mapEvent(ev, device):
                device.outDevice.write_event(e)
            device.outDevice.syn()
    except Exception as e:
        log.error(f'An Exception occurred on Device: {device.name}\n{e}\n')
        log.debug(f'traceback for exception: {e}\n{traceback.format_exc()}')


class Device(yaml.YAMLObject):
    """
        This is a class designed to hold the information regarding a particular device. It is loaded in via a yaml
        config file located inside 'devices.d'. The file will need to contain 'vendorid', 'productid', and 'name'.
        Keys are optional and is suppose to be a dictionary.
    """
    yaml_tag = u'!Device'

    vendorid = None
    productid = None
    name = None
    keys = None
    type = None
    keymapper = None
    deviceKeyMap = None

    evdevice = None
    outDevice = None

    def __init__(self, vendorid, productid, name, type=None, keys=None):
        """
            This is not used by yaml when creating the Device object. Do not edit this to troubleshoot unless you
            intend to 'manually' create a Device class.
        :param vendorid: int
        :param productid: int
        :param name: str
        :param keys: dictionary
        """
        self.vendorid = str(vendorid)
        self.productid = str(productid)
        self.name = name
        self.type = type
        self.evdevice = None
        if keys is None:
            self.keys = {}
        else:
            self.keys = keys

    def __hash__(self):
        return hash(self.name)

    def setup(self, keymapper, inputDevices):
        """
            Used by the DeviceManager. This checks things and finishes setting up the Device with the necessary
        :param keymapper: KeyMapper object
        :param inputDevices: List of InputDevices from evdev.
        :return: None
        """
        self.checkDeviceVariables()
        self.findDevice(inputDevices)
        if self.isValid:    # Continue if 'findDevice' found the input devices on the OS.
            self.setKeyMapper(keymapper)
            self.generateOuputDevice()

    def setKeyMapper(self, keymapper):
        """
            This sets the keymapper and gets back a dictionary of mapped keys
        :param keymapper: KeyMapper class object
        :return: None
        """
        self.keymapper = keymapper
        self.deviceKeyMap = self.keymapper.addDeviceKeyMapping(self, self.keys)

    def checkDeviceVariables(self):
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

    def findDevice(self, deviceList):
        """
            This is called by the DeviceManager class. The Device tries to find the associated 'input' IO files on the
            OS that are linked to the device in question. It compares the vendorid and productid which both have to
            match. There are devices that create multiple inputs. This links them together.
        :param deviceList:
        :return:
        """
        self.evdevice = None
        for dev in deviceList:
            if self.vendorid in Device._toHex(dev.info.vendor) and self.productid in Device._toHex(dev.info.product):
                log.info(f'Found device {dev}.')
                if self.type == self.getDeviceType(dev):
                    if self.evdevice is not None:
                        raise Exception("This device was found more then once!")
                    self.evdevice = dev
        return self.evdevice

    def mapEvent(self, event):
        """
            This is called upon by the DeviceInputWorker associated with this Device. The job is to check to see if the
            event sent (key pressed) is associated with a map.
        :param event: InputEvent object
        :return: InputEvent object
        """
        return self.keymapper.mapEvent(event, self)

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

    def generateOuputDevice(self):
        """
            This creates a new Output device on the OS that takes on the capabilities of the input devices associated
            with this device.
        :return:
        """
        self.outDevice = UInput.from_device(self.evdevice, name=self.name + '_output')

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
    def isKeyboard(device):
        return len(device.capabilities().get(1, [])) > 160

    @staticmethod
    def isMouse(device):
        return len(device.capabilities().get(2, [])) > 1

    @staticmethod
    def getDeviceType(device):
        if Device.isKeyboard(device) and Device.isMouse(device):
            return 'both'
        elif Device.isKeyboard(device):
            return 'EV_KEY'
        elif Device.isMouse(device):
            return 'EV_BUTTON'
        return 'both'

    @staticmethod
    def _toHex(hexString, standardLength=4):
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
            This requires both the config load and the keymapper. It will use the configLoader to load all the different
            devicename.yaml config files noted in the main.yaml. Each one should load a new Device class. It will pass
            the keymapper along to the different devices it finds.
            NOTE: the 'inputDevices' variable that is set actually is a list of all known input devices on the box. Each
                device will look through that list to try to find its device. This is a large point of failure.
        :param settingsManager: SettingsManager object
        :param keymapper: KeyMapper object
        """
        self.settings = settingsManager
        self.keymapper = keymapper
        self.inputDevices = [InputDevice(fn) for fn in evdev.list_devices()]
        self.getDeviceConfigs()

    def __str__(self):
        return '\n'.join([f"{dev.path} - {dev.name} - {Device._toHex(dev.info.vendor)}:"
                          f"{Device._toHex(dev.info.product)}"
                          for dev in self.inputDevices])

    def getDeviceConfigs(self):
        """
            This uses the SettingsManager protected variable 'devices' to grab the list of yaml config files from the
            main.yaml config file. It will run the 'loadConfig' method from SettingsManager with the parameter
            'device=True' for each yaml config file it sees. It will then iterate through the nearly created list of
            devices and run a series of methods on them setting them up.
        :return:
        """
        self.devices = []
        for device in self.settings.devices:
            self.devices.append(self.settings.loadYaml(device, device=True))
        for device in self.devices:
            device.setup(self.keymapper, self.inputDevices)
        return self.devices

    def findDevices(self):
        for device in self.devices:
            device.findDevice(self.inputDevices)

    def grabDevices(self):
        log.info("Grabbing all configured devices")
        for device in self.devices:
            device.grab()

    def ungrabDevices(self):
        log.info("Releasing all configured devices")
        for device in self.devices:
            device.ungrab()

    def closeDevices(self):
        log.info("Closing all evdev UInput devices")
        for device in self.devices:
            device.close()
        while len(self.devices) > 0:
            item = self.devices.pop()
            del item

    def deleteInputs(self):
        log.info("Deleting all Input Devices")
        for item in self.inputDevices:
            item.close()
        while len(self.inputDevices) > 0:
            item = self.inputDevices.pop()
            del item
