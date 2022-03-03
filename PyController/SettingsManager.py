#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description: This package loads the configuration files.


import os
import sys
import logging
import yaml
from gi.repository import GLib


defaultMainConfigFile = "main.yaml"
deviceDir = "devices.d/"
profileDir = "profiles.d/"
mainConfigExample = """main:
  deviceDir: 'devices.d' # Currently, this cannot be changed.
  profileDir: 'profiles.d' # Currently, this cannot be changed.
  logging: False
  loglevel: "CRITICAL" # DEBUG, INFO, WARNING, ERROR, CRITICAL (DEBUG is the most verbose)
devices:
# - exampleDevice.yaml
profiles:
#  - exampleProfile.yaml
"""


log = logging.getLogger('ConfigLoader')


class SettingsManager(object):

    arguments = None
    installDir = None
    configDir = None
    mainConfigFile = None
    mainConfig = None
    profilesConfig = None

    def __init__(self, arguments, install_dir=None):
        """
            This whole classes job is to pull yaml config files particular the main.yaml which has a series of
            'shortcut' protected variables to grab the useful information out of the main.yaml config file.
        """
        super().__init__()
        self.configDir = os.path.join(GLib.get_user_config_dir(), 'PyController/')
        self.installDir = install_dir if install_dir else os.path.realpath(sys.path[0])
        self.mainConfigFile = os.path.join(self.configDir + defaultMainConfigFile)
        if not os.path.exists(self.configDir) or not os.path.exists(self.mainConfigFile):
            self.setup_configs()
        self.arguments = arguments
        self.load_main_config()
        self.load_profiles()

    def setup_configs(self):
        if not os.path.exists(self.configDir):
            os.makedirs(self.configDir)
        if not os.path.exists(self.mainConfigFile):
            with open(self.mainConfigFile, 'w') as confFile:
                confFile.write(mainConfigExample)
        if not os.path.exists(os.path.join(self.configDir, deviceDir)):
            os.makedirs(os.path.join(self.configDir, deviceDir))
        if not os.path.exists(os.path.join(self.configDir, profileDir)):
            os.makedirs(os.path.join(self.configDir, profileDir))
        if not os.path.exists(os.path.join(self.configDir, deviceDir, 'exampleDevice.yaml')):
            if os.path.exists(os.path.join(self.installDir, deviceDir, 'exampleDevice.yaml')):
                os.system(f"cp "
                          f"{os.path.join(self.installDir, deviceDir, 'exampleDevice.yaml')} "
                          f"{os.path.join(self.configDir, deviceDir, 'exampleDevice.yaml')}")
        if not os.path.exists(os.path.join(self.configDir, profileDir, 'exampleProfile.yaml')):
            if os.path.exists(os.path.join(self.installDir, profileDir, 'exampleProfile.yaml')):
                os.system(f"cp "
                          f"{os.path.join(self.installDir, profileDir, 'exampleProfile.yaml')} "
                          f"{os.path.join(self.configDir, profileDir, 'exampleProfile.yaml')}")

    def show_config_path(self):
        return f"\n{self.mainConfigFile if self.arguments.config == defaultMainConfigFile else self.arguments.config}\n"

    def load_main_config(self):
        """
            This logs the main config file. This is necessary for the program to work.
        :return: None
        """
        configfile = self.mainConfigFile if self.arguments.config == defaultMainConfigFile else self.arguments.config
        log.info("Loading main config file: %s" % configfile)
        self.mainConfig = self.load_yaml(configfile)
        assert isinstance(self.mainConfig, dict)

    def load_profiles(self):
        self.profilesConfig = {}
        for profile in self.profiles:
            self.profilesConfig.update(self.load_yaml(profile, profile=True))

    def config_loader(self, filepath, device=False, profile=False):
        """
            This method loads a file from disk and returns it. By default the load_yaml parameter is set to True so the
            method will first try to pass the file contents through 'yaml.load' and then return that.
        :param filepath: str: a filename
        :param device: bool: Default False: Tells the method to pre-append the deviceDir to the filename.
        :param profile: bool: Default False: Tells the method to pre-append the profileDir to the filename.
        :return: dict or str
        """
        if not os.path.isabs(filepath):
            if device:
                filepath = os.path.join(self.configDir, self.deviceDir, filepath)
            elif profile:
                filepath = os.path.join(self.configDir, self.profileDir, filepath)
            else:
                filepath = os.path.join(self.configDir, filepath)
        with open(filepath) as f:
            config = f.read()
        return config

    def load_yaml(self, file, *args, **kwargs):
        return yaml.load(self.config_loader(file, *args, **kwargs), Loader=yaml.Loader)

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
            return set()
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
