#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This package loads the configuration files.


import logging
import yaml


mainConfigFile = "main.yaml"
deviceDir = "devices.d/"
profileDir = "profiles.d/"


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('ConfigLoader')


class ConfigLoader(object):

    mainConfig = None

    def __init__(self):
        super(ConfigLoader, self).__init__()
        self.loadMainConfig()

    def loadMainConfig(self):
        self.mainConfig = self.loadConfig(mainConfigFile)

    def loadConfig(self, filepath, loadYaml=True, device=False, profile=False):
        if device:
            filepath = deviceDir + filepath
        elif profile:
            filepath = profileDir + filepath
        with file(filepath) as f:
            config = f.read()
        if loadYaml:
            return yaml.load(config)
        return config

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
