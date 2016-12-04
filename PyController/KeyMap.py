#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description: This package holds the code for mapping keys so that one can.


import logging
from evdev import InputEvent, ecodes


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('KeyMapper')


class KeyMapper(object):
    """
        This class is designed to keep track of all the key mappings and to map any key.
    """

    deviceKeyMap = None
    profileKeyMap = None
    settings = None
    down = long(1)
    up = long(0)

    def __init__(self, settings):
        """
            This uses the SettingsManager to grab profile.d information
        :param settings: SettingsManager object
        """
        super(KeyMapper, self).__init__()
        self.settings = settings
        self.deviceKeyMap = {}
        self.profileKeyMap = {}

    def addDeviceKeyMapping(self, deviceName, keys):
        """
            This creates a dictionary of key mappings for a particular device.
        :param deviceName: str
        :param keys: dictionary
        :return: dictionary
        """
        self.deviceKeyMap[deviceName] = {}
        for inputKey, mapKey in keys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                continue
            self.deviceKeyMap[deviceName][getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)
        return self.deviceKeyMap[deviceName]

    def updateProfileKeyMap(self, profileKeys):
        """
            This updates the 'profileKeyMap' variable with more key mappings.
        :param profileKeys: dictionary
        :return: None
        """
        self.profileKeyMap = {}
        for inputKey, mapKey in profileKeys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                log.warn("This key map pair is invalid - Input Key: %s Replacement Key: %s" % (inputKey, mapKey))
                continue
            self.profileKeyMap[getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)

    def mapEvent(self, event, deviceKeyMap):
        """
            This takes an event and a deviceKeyMap. The method first checks the profileKeyMap and will ignore the
            deviceKeyMap as anything in a profile should override the device settings.
        :param event: InputEvent object
        :param deviceKeyMap: dictionary supplies by a Device
        :return: InputEvent
        """
        if event.code in self.profileKeyMap:
            log.debug("Profile key mapping of: %s was detected replacing it for %s" %
                      (event.code, self.profileKeyMap[event.code]))
            return InputEvent(event.sec, event.usec, ecodes.EV_KEY, self.profileKeyMap[event.code], event.value)
        elif event.code in deviceKeyMap:
            log.debug("Device key mapping of: %s was detected replacing it for %s" %
                      (event.code, deviceKeyMap[event.code]))
            return InputEvent(event.sec, event.usec, ecodes.EV_KEY, deviceKeyMap[event.code], event.value)
        return event

    @staticmethod
    def validateKeyPair(inputKey, mapKey):
        """
            A simple little validator. This makes sure that the key and the key you want to map it to are valid.
            NOTE: This is a failure point. If you put a key in here that isn't registered by evdev.ecodes then it will
                not be added to the map. This may be why it wont map.
        :param inputKey: str
        :param mapKey: str
        :return: bool
        """
        return hasattr(ecodes, inputKey) and hasattr(ecodes, mapKey)
