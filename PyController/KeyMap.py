#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This package holds the code for mapping keys so that one can.


import logging
from evdev import InputEvent, ecodes


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('KeyMapper')


class KeyMapper(object):

    deviceKeyMap = None
    profileKeyMap = None
    settings = None
    down = long(1)
    up = long(0)

    def __init__(self, settings):
        super(KeyMapper, self).__init__()
        self.settings = settings
        self.deviceKeyMap = {}
        self.profileKeyMap = {}

    def addDeviceKeyMapping(self, deviceName, keys):
        self.deviceKeyMap[deviceName] = {}
        for inputKey, mapKey in keys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                continue
            self.deviceKeyMap[deviceName][getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)
        return self.deviceKeyMap[deviceName]

    def updateProfileKeyMap(self, profileKeys):
        self.profileKeyMap = {}
        for inputKey, mapKey in profileKeys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                continue
            self.profileKeyMap[getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)

    def mapEvent(self, event, deviceKeyMap):
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
        return hasattr(ecodes, inputKey) and hasattr(ecodes, mapKey)
