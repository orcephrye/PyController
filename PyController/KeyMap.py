#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description: This package holds the code for mapping keys so that one can.


import logging
import time
from evdev import InputEvent, ecodes


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

    def add_device_keymap(self, device, keys):
        """
            This creates a dictionary of key mappings for a particular device.

        :param device: str
        :param keys: dictionary
        :return: dictionary
        """

        log.info(f"Building keymap for [{device}] with keys: {keys}")

        if device not in self.deviceKeyMap:
            self.deviceKeyMap[device] = {}

        for inputKey, mapKey in keys.items():
            if not KeyMapper.validate_key_pair(inputKey, mapKey):
                log.warning(f'The key map of input: {inputKey} mapped to {mapKey} failed validation.')
                continue

            self.deviceKeyMap[device][getattr(ecodes, inputKey)] = InputEvent(time.time(),
                                                                              0,
                                                                              ecodes.EV_KEY,
                                                                              getattr(ecodes, mapKey),
                                                                              1)

        return self.deviceKeyMap[device]

    def add_profile_keymap(self, profileKeys, profileName, deviceName=None):
        """
            This updates the 'profileKeyMap' variable with more key mappings.
        :param profileKeys: dictionary
        :param profileName: str
        :return: None
        """

        if profileName not in self.profileKeyMap:
            self.profileKeyMap[profileName] = {}

        if deviceName is not None and deviceName not in self.profileKeyMap[profileName]:
            self.profileKeyMap[profileName][deviceName] = {}

        for inputKey, mapKey in profileKeys.items():
            if not KeyMapper.validate_key_pair(inputKey, mapKey):
                log.warning(f'The key map of input: {inputKey} mapped to {mapKey} failed validation.')
                continue
            self.profileKeyMap[profileName][getattr(ecodes, inputKey)] = InputEvent(time.time(),
                                                                                    0,
                                                                                    ecodes.EV_KEY,
                                                                                    getattr(ecodes, mapKey),
                                                                                    1)

    def make_profile_active(self, profileName):
        """
            This checks the name provided by the config file against the profileKeys dictionary and if it exists sets
            the activeProve variable to it.
        :param profileName: (str)
        :return:
        """
        if profileName in self.profileKeyMap:
            log.info(f'Setting new active profile: {profileName}')
            log.debug(f'The new profile settings to be used: {self.profileKeyMap.get(profileName)}')
            self.activeProfile = profileName

    def deactivate_profile(self, profileName):
        if profileName == self.activeProfile:
            log.info(f'Deactivating profile: {profileName}')
            self.activeProfile = None

    def map_event(self, event, device):
        """
            This takes an event and a deviceKeyMap. The method first checks the profileKeyMap and will ignore the
            deviceKeyMap as anything in a profile should override the device settings.
        :param event: InputEvent object
        :param device: Device object
        :return: InputEvent
        """
        if event.type != ecodes.EV_KEY:
            return event

        rEvent = self.get_active_profile_for_device(device, event.code) or \
                 self.deviceKeyMap[device].get(event.code, None)

        if rEvent is None:
            return event

        rEvent.sec = event.sec
        rEvent.usec = event.usec + 25
        rEvent.value = event.value
        return rEvent

    def get_active_profile_for_device(self, device, code):
        return self.profile.get(device.name, {}).get(code, None) or self.profile.get(code, None)


    @staticmethod
    def validate_key_pair(inputKey, mapKey):
        """
            A simple little validator. This makes sure that the key and the key you want to map it to are valid.
            NOTE: This is a failure point. If you put a key in here that isn't registered by evdev.ecodes then it will
                not be added to the map. This may be why it wont map.
        :param inputKey: str
        :param mapKey: str
        :return: bool
        """
        return hasattr(ecodes, inputKey) and hasattr(ecodes, mapKey)

    @property
    def profile(self):
        return self.profileKeyMap.get(self.activeProfile) or {}
