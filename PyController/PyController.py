#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
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


class PyGamePad(object):

    killer = None
    settings = None
    devManager = None
    devWorkers = None
    keymapper = None

    def __init__(self):
        self.killer = GracefulKiller()
        self.settings = Settings()
        self.configureLogging()
        self.keymapper = KeyMapper(self.settings)
        self.devManager = DeviceManager(self.settings, self.keymapper)
        self.devWorkers = []

    def preRunCheck(self):
        pass

    def run(self):
        log.info("Starting PyController!")
        self.devManager.grabDevices()

        log.info("Starting Device Input Worker Threads")
        for device in self.devManager.devices:
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
    PyGamePad().run()
