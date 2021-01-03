#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description: This package loads the configuration files.


import logging
import yaml


mainConfigFile = "main.yaml"
deviceDir = "devices.d/"
profileDir = "profiles.d/"


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('ConfigLoader')


class SettingsManager(object):

    mainConfig = None
    profilesConfig = None

    def __init__(self):
        """
            This whole classes job is to pull yaml config files particular the main.yaml which is has a series of
            'shortcut' protected variables to grab the useful information out of the main.yaml config file.
        """
        super().__init__()
        self.loadMainConfig()
        self.loadProfiles()

    def loadMainConfig(self):
        """
            This logs the main config file. This is necessary for the program to work.
        :return: None
        """
        log.info("Loading main config file: %s" % mainConfigFile)
        self.mainConfig = SettingsManager.loadYaml(mainConfigFile)
        assert isinstance(self.mainConfig, dict)

    def loadProfiles(self):
        self.profilesConfig = {}
        for profile in self.profiles:
            self.profilesConfig.update(SettingsManager.loadYaml(profile, profile=True))

    @staticmethod
    def configLoader(filepath, device=False, profile=False):
        """
            This method loads a file from disk and returns it. By default the loadYaml parameter is set to True so the
            method will first try to pass the file contents through 'yaml.load' and then return that.
        :param filepath: str: a filename
        :param load_yaml: bool: Default True. Tells the method whether to pass the file contents through 'yaml.load'.
        :param device: bool: Default False: Tells the method to pre-append the deviceDir to the filename.
        :param profile: bool: Default False: Tells the method to pre-append the profileDir to the filename.
        :return: dict or str
        """
        if device:
            filepath = deviceDir + filepath
        elif profile:
            filepath = profileDir + filepath
        with open(filepath) as f:
            config = f.read()
        return config

    @staticmethod
    def loadYaml(file, *args, **kwargs):
        return yaml.load(SettingsManager.configLoader(file, *args, **kwargs), Loader=yaml.Loader)

    @property
    def devices(self):
        if not self.mainConfig:
            return []
        return self.mainConfig.get('devices', []) or []

    @property
    def profiles(self):
        if not self.mainConfig:
            return []
        return self.mainConfig.get('profiles', []) or []

    @property
    def games(self):
        if not self.profilesConfig:
            return []
        outGames = []
        for game in [profile['executable'] for profile in self.profilesConfig.values() if 'executable' in profile]:
            if type(game) is list:
                outGames.extend(game)
            else:
                outGames.append(game)
        return set(map(str.lower, outGames))

    @property
    def deviceDir(self):
        try:
            return self.mainConfig['main']['devicesDir']
        except Exception:
            return deviceDir

    @property
    def profileDir(self):
        try:
            return self.mainConfig['main']['profileDir']
        except Exception:
            return profileDir

    @property
    def logging(self):
        try:
            return self.mainConfig['main']['logging']
        except Exception:
            return False

    @property
    def loggingLevel(self):
        try:
            return self.mainConfig['main']['loglevel']
        except Exception:
            return 'ERROR'

    @property
    def logFile(self):
        try:
            return self.mainConfig['main']['logFile']
        except Exception:
            return ''
