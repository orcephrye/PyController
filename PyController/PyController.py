#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description: This is a game pad key mapping tool may originally for the Razor Nostromo to run on Linux.


import logging
import signal
from time import sleep
from threading import Lock
from Devices import DeviceManager
from DeviceWorker import DeviceInputWorker as DIW
from SettingsManager import SettingsManager as Settings
from KeyMap import KeyMapper

log = logging.getLogger('PyControlMain')


class GracefulKiller(object):
    """
        This class is designed to be instatiated once and then passed around to all the DeviceInputWorker classes to be
        used as a stop gap for when a kill signal as been received. It is also used in the 'run' method of the
        PyController class. It simply changes the 'kill_now' from a False to a True allowing for a while loop to exit.
    """

    kill_now = None
    _kill_now = None
    __LOCK__ = None

    def __init__(self):
        self.__LOCK__ = Lock()
        self.kill_now = False
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        log.info("A Kill signal has been received.")
        self.kill_now = True

    @property
    def kill_now(self):
        try:
            with self.__LOCK__:
                return self._kill_now
        except RuntimeError:
            pass

    @kill_now.setter
    def kill_now(self, value):
        try:
            with self.__LOCK__:
                self._kill_now = value
        except RuntimeError:
            pass

    @kill_now.deleter
    def kill_now(self):
        try:
            with self.__LOCK__:
                self._kill_now = None
        except RuntimeError:
            pass


class PyController(object):
    """
        The main function of the PyController project. This sets up all the other packages and 'gets the ball rolling'.
        It takes no arguments but uses the SettingsManager class to pull settings from the main.yaml config file.
    """

    killer = None
    settings = None
    devManager = None
    devWorkers = None
    keymapper = None

    def __init__(self):
        self.killer = GracefulKiller()  # This is passed along to all the DeviceInputWorkers
        self.settings = Settings()  # This is passed to the KeyMapper and to the DeviceManager
        self.configureLogging()  # This uses the Settings manager to set the logging settings
        self.keymapper = KeyMapper(self.settings)   # This is used by the DeviceManager and is passed to each Device
        self.devManager = DeviceManager(self.settings, self.keymapper)  # This setups all the devices found in devices.d
        self.devWorkers = []    # This is where the DeviceInputWorkers are stored

    def preRunCheck(self):
        pass

    def run(self):
        """
            This grabs the devices from devManager and then starts all the DeviceInputWorkers. It then sits in a while
            loop waiting for a kill signal. Its job once the signal is received is to clean up by exiting the DIWs,
            releasing grabbed devices and closing any created input devices.
        :return: None
        """
        log.info("Starting PyController!")
        self.devManager.grabDevices()

        log.info("Starting Device Input Worker Threads")
        for device in self.devManager.devices:
            if device.isValid:
                self.devWorkers.append(DIW(device, killer=self.killer))

        while not self.killer.kill_now:
            sleep(1)

        log.info("Killing Device Input Worker Threads")
        for worker in self.devWorkers:
            worker.join(timeout=1)

        self.devManager.ungrabDevices()
        self.devManager.closeDevices()
        log.info("Ending PyController!")
        return

    def configureLogging(self):
        """
            Sets up the logging for the box. Gets its configuration information from SettingsManager which gets its info
            from main.yaml
        :return: None
        """
        if self.settings.logging:
            loglevel = getattr(logging, self.settings.loggingLevel, 40) or 40
            if self.settings.logFile:
                logging.basicConfig(filename=self.settings.logFile,
                                    format='%(module)s %(funcName)s %(lineno)s %(message)s', level=loglevel)
            else:
                logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=loglevel)
        else:
            logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=100)


if __name__ == '__main__':
    PyController().run()
