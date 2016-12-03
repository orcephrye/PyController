#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This package holds the Device class which keeps information about a particular device.


import yaml
import evdev
from evdev import InputDevice


class Device(yaml.YAMLObject):
    yaml_tag = u'!Device'

    vendorid = None
    productid = None
    name = None
    keys = None

    device = None

    def __init__(self, vendorid, productid, name, keys=None):
        self.vendorid = str(vendorid)
        self.productid = str(productid)
        self.name = name
        if keys is None:
            self.keys = {}
        else:
            self.keys = keys

    def _checkDeviceVariables(self):
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

    def grabDevice(self):
        for dev in self.device:
            dev.grab()

    def ungrabDevice(self):
        for dev in self.device:
            dev.ungrab()

    @staticmethod
    def _toHex(hexString, standardLength=4):
        return hex(hexString)[2:].rjust(standardLength, '0')


class DeviceManager(object):

    configLoader = None
    inputDevices = None
    devices = None

    def __init__(self, configLoader):
        self.configLoader = configLoader
        self.inputDevices = [InputDevice(fn) for fn in evdev.list_devices()]
        self.getDeviceConfigs()

    def getDeviceConfigs(self):
        self.devices = []
        for device in self.configLoader.devices:
            self.devices.append(self.configLoader.loadConfig(device, device=True))
        return self.devices

    def findDevices(self):
        for device in self.devices:
            device.findDevice(self.inputDevices)

    def grabDevices(self):
        for device in self.devices:
            device.grabDevice()

    def ungrabDevices(self):
        for device in self.devices:
            device.ungrabDevice()
