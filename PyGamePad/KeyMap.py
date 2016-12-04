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
    down = long(1)
    up = long(0)

    def __init__(self):
        super(KeyMapper, self).__init__()
        self.deviceKeyMap = {}
        self.profileKeyMap = {}

    def addDeviceKeyMapping(self, deviceName, keys):
        self.deviceKeyMap[deviceName] = {}
        for inputKey, mapKey in keys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                continue
            self.deviceKeyMap[deviceName][getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)

    def updateProfileKeyMap(self, profileKeys):
        self.profileKeyMap = {}
        for inputKey, mapKey in profileKeys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                continue
            self.profileKeyMap[getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)

    def mapEvent(self, event, device):
        keymap = self.deviceKeyMap.get(device, {}) or {}
        keymap.update(self.profileKeyMap)
        if event.code in keymap:
            return InputEvent(event.sec, event.usec, ecodes.EV_KEY, keymap[event.code], event.value)
        return event

    @staticmethod
    def validateKeyPair(inputKey, mapKey):
        return hasattr(ecodes, inputKey) and hasattr(ecodes, mapKey)
