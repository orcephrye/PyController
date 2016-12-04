#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This package holds the Device class which keeps information about a particular device.


import logging
import yaml
import evdev
from evdev import InputDevice, UInput


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('Device')


class Device(yaml.YAMLObject):
    yaml_tag = u'!Device'

    vendorid = None
    productid = None
    name = None
    keys = None
    keymapper = None
    deviceKeyMap = None

    device = None
    outDevice = None

    def __init__(self, vendorid, productid, name, keys=None):
        self.vendorid = str(vendorid)
        self.productid = str(productid)
        self.name = name
        if keys is None:
            self.keys = {}
        else:
            self.keys = keys

    def setKeyMapper(self, keymapper):
        self.keymapper = keymapper
        self.deviceKeyMap = self.keymapper.addDeviceKeyMapping(self.name, self.keys)

    def checkDeviceVariables(self):
        self.vendorid = str(self.vendorid)
        self.productid = str(self.productid)
        self.name = str(self.name)
        if self.keys is None or type(self.keys) is not dict:
            self.keys = {}

    def findDevice(self, deviceList):
        self.device = []
        for dev in deviceList:
            if self.vendorid in Device._toHex(dev.info.vendor) and self.productid in Device._toHex(dev.info.product):
                self.device.append(dev)
        return self.device

    def mapEvent(self, event):
        return self.keymapper.mapEvent(event, self.deviceKeyMap)

    def grab(self):
        log.info("Grabbing input devices associated with: %s" % self.name)
        for dev in self.device:
            dev.grab()

    def ungrab(self):
        log.info("Releasing input devices associated with: %s" % self.name)
        for dev in self.device:
            dev.ungrab()

    def close(self):
        log.info("Closing output devices associated with: %s" % self.name)
        self.outDevice.close()

    def generateOuputDevice(self):
        self.outDevice = UInput.from_device(*self.device, name=self.name + '_input')

    @staticmethod
    def _toHex(hexString, standardLength=4):
        return hex(hexString)[2:].rjust(standardLength, '0')


class DeviceManager(object):

    configLoader = None
    inputDevices = None
    keymapper = None
    devices = None

    def __init__(self, configLoader, keymapper):
        self.configLoader = configLoader
        self.keymapper = keymapper
        self.inputDevices = [InputDevice(fn) for fn in evdev.list_devices()]
        self.getDeviceConfigs()

    def getDeviceConfigs(self):
        self.devices = []
        for device in self.configLoader.devices:
            self.devices.append(self.configLoader.loadConfig(device, device=True))
        for device in self.devices:
            device.findDevice(self.inputDevices)
            device.checkDeviceVariables()
            device.setKeyMapper(self.keymapper)
            device.generateOuputDevice()
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
