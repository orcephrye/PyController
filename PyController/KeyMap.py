#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description: This package holds the code for mapping keys so that one can.


import logging
import time
from evdev import InputEvent, ecodes


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('KeyMapper')


class KeyMapper(object):
    """
        This class is designed to keep track of all the key mappings and to map any key.
    """

    deviceKeyMap = None
    profileKeyMap = None
    activeProfile = None
    settings = None

    def __init__(self, settings):
        """
            This uses the SettingsManager to grab profile.d information
        :param settings: SettingsManager object
        """
        super(KeyMapper, self).__init__()
        self.settings = settings
        self.deviceKeyMap = {}
        self.profileKeyMap = {}

    def addDeviceKeyMapping(self, device, keys):
        """
            This creates a dictionary of key mappings for a particular device.
        :param device: str
        :param keys: dictionary
        :return: dictionary
        """
        if device.type == 'EV_KEY':
            self.deviceKeyMap[device] = {i: (i, ) for i in device.evdevice.capabilities().get(1, [])}
        elif device.type == 'EV_BUTTON':
            self.deviceKeyMap[device] = {i: (i, ) for i in device.evdevice.capabilities().get(2, [])}
        else:
            raise ValueError(f'The device.type is: {device.type} but it needs to be ether EV_KEY or EV_BUTTON')

        # log.debug(f'The capabilities of the evdevice: {device} is: {self.deviceKeyMap[device]}')

        for inputKey, mapKey in keys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                log.warning(f'The key map of input: {inputKey} mapped to {mapKey} failed validation.')
                continue
            if type(mapKey) is list:
                self.deviceKeyMap[device][getattr(ecodes, inputKey)] = tuple([getattr(ecodes, i) for i in mapKey])
            else:
                self.deviceKeyMap[device][getattr(ecodes, inputKey)] = (getattr(ecodes, mapKey), )

        for inputKey, outputKeyTuple in self.deviceKeyMap[device].items():
            self.deviceKeyMap[device][inputKey] = tuple([InputEvent(time.time(), 0, ecodes.EV_KEY, key, 1)
                                                         for key in outputKeyTuple])

        return self.deviceKeyMap[device]

    def updateProfileKeyMap(self, profileKeys, profileName):
        """
            This updates the 'profileKeyMap' variable with more key mappings.
        :param profileKeys: dictionary
        :return: None
        """
        self.profileKeyMap = {}
        for inputKey, mapKey in profileKeys.items():
            if not KeyMapper.validateKeyPair(inputKey, mapKey):
                log.warning("This key map pair is invalid - Input Key: %s Replacement Key: %s" % (inputKey, mapKey))
                continue
            self.profileKeyMap[getattr(ecodes, inputKey)] = getattr(ecodes, mapKey)
        self.activeProfile = profileName

    def removeProfile(self, profileName):
        if profileName == self.activeProfile:
            self.profileKeyMap = {}
            self.activeProfile = None

    def mapEvent(self, event, device):
        """
            This takes an event and a deviceKeyMap. The method first checks the profileKeyMap and will ignore the
            deviceKeyMap as anything in a profile should override the device settings.
        :param event: InputEvent object
        :param device: Device object
        :return: InputEvent
        """
        if event.type != ecodes.EV_KEY:
            # log.debug(f'The event ({event}) was received and returned')
            yield event
        else:
            currentTime = event.sec
            currentUsec = event.usec
            for returnEvent in self.deviceKeyMap[device].get(event.code, ()):
                if type(returnEvent) is float:
                    time.sleep(returnEvent)
                    continue
                returnEvent.sec = currentTime
                currentUsec += 100
                returnEvent.usec = currentUsec
                returnEvent.value = event.value
                log.debug(f'The event ({event}) was received and has been mapped too: ({returnEvent})')
                yield returnEvent

        # if event.code in self.profileKeyMap:
        #     log.debug("Profile key mapping of: %s was detected replacing it for %s" %
        #               (event.code, self.profileKeyMap[event.code]))
        #     event.code = self.profileKeyMap[event.code]
        # elif event.code in self.deviceKeyMap[device]:
        #     log.debug("Device key mapping of: %s was detected replacing it for %s" %
        #               (event.code, self.deviceKeyMap[event.code]))
        #     if type(self.deviceKeyMap[event.code]) is list:
        #         tempUsec = event.usec
        #         tempList = []
        #         for code in self.deviceKeyMap[event.code]:
        #             tempUsec += 100
        #             tempList.append(InputEvent(event.sec, tempUsec, ecodes.EV_KEY, code, event.value))
        #         return tempList
        #     event.code = self.deviceKeyMap[event.code]
        # return event

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
        if type(mapKey) is list:
            for mapk in mapKey:
                if not hasattr(ecodes, mapk):
                    return False
            return hasattr(ecodes, inputKey)
        return hasattr(ecodes, inputKey) and hasattr(ecodes, mapKey)
