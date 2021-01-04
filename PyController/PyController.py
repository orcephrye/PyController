#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.3
# Date: 12/01/2016
# Description: This is a game pad key mapping tool may originally for the Razor Nostromo to run on Linux.


import logging
import signal
import asyncio
import warnings
import traceback
from multiprocessing import Process, Value, Queue
from PyDevices import DeviceManager, AsyncDeviceWorker
from SettingsManager import SettingsManager as Settings
from GameMonitor import GameMonitor
from KeyMap import KeyMapper


log = logging.getLogger('PyControlMain')
warnings.filterwarnings("ignore", category=RuntimeWarning)


kill_now = Value('i', 1)
globalQueue = Queue()


def dummyFunction(*args, **kwargs):
    log.warning(f'This dummy function was called which should never happen')


class GracefulKiller(object):
    """
        This class is designed to be instantiated once and then passed around to all the DeviceInputWorker classes to be
        used as a stop gap for when a kill signal as been received. It is also used in the 'run' method of the
        PyController class. It simply changes the 'kill_now' from a False to a True allowing for a while loop to exit.
    """

    pyc = None
    loop = None

    def __init__(self, pyc, loop):
        self.pyc = pyc
        self.loop = loop
        self.loop.add_signal_handler(signal.SIGINT, asyncio.ensure_future, self.exit_gracefully())
        self.loop.add_signal_handler(signal.SIGTERM, asyncio.ensure_future, self.exit_gracefully())

    async def exit_gracefully(self):
        log.info("A Kill signal has been received.")
        global kill_now
        kill_now.value = 0
        for task in pyc.devWorkers:
            task.cancel()
        for task in pyc.devWorkers:
            await task


class PyController(object):
    """
        The main class of the PyController project. This sets up all the other packages and 'gets the ball rolling'.
        It takes no arguments but uses the SettingsManager class to pull settings from the main.yaml config file.
    """

    killer = None
    settings = None
    devManager = None
    devWorkers = None
    keymapper = None
    asyncLoop = None

    def __init__(self):
        self.settings = Settings()  # This is passed to the KeyMapper and to the DeviceManager
        self.configureLogging()  # This uses the Settings manager to set the logging settings
        self.keymapper = KeyMapper(self.settings)   # This is used by the DeviceManager and is passed to each Device
        self.devManager = DeviceManager(self.settings, self.keymapper)  # This setups all the devices found in devices.d
        self.devWorkers = []    # This is where the AsyncDeviceWorker coroutines/tasks are stored

    async def setup(self, killer):
        log.info("Setting up PyController!")
        self.killer = killer
        self.devManager.grabDevices()

        log.info("Making Device Input Tasks")
        for device in self.devManager.devices:
            if device.isValid:
                self.devWorkers.append(asyncio.create_task(AsyncDeviceWorker(device)))

        return self.devWorkers

    async def run(self, killer):
        """
            This grabs the devices from devManager and then starts all the DeviceInputWorkers. It then sits in a while
            loop waiting for a kill signal. Its job once the signal is received is to clean up by exiting the DIWs,
            releasing grabbed devices and closing any created input devices.
        :return: None
        """
        await self.setup(killer)

        log.info("Gathering all device workings and running them")
        self.devWorkers.append(asyncio.create_task(self.gameMonitor()))
        log.debug(f'Workers: {self.devWorkers}')
        await asyncio.wait(self.devWorkers, return_when=asyncio.FIRST_EXCEPTION)
        log.info("Finished now exiting")

        await self.shutdown()

    async def shutdown(self):
        log.info("Disconnecting Devices")
        self.devManager.ungrabDevices()
        self.devManager.closeDevices()
        log.info("Ending PyController!")

    async def gameMonitor(self):
        global globalQueue
        while bool(kill_now.value):
            if not globalQueue.empty():
                try:
                    value = globalQueue.get_nowait()
                    log.debug(f'The received value is: {value}')
                    getattr(self.keymapper, value[0], dummyFunction)(value[1])
                except Exception as e:
                    log.error(f'Error in gameMonitor main method: {e}')
                    log.debug(f'[DEBUG] for gameMonitor main method: {traceback.format_exc()}')
            await asyncio.sleep(5)

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
    try:
        loop = asyncio.get_event_loop()
        pyc = PyController()
        p = None
        if pyc.settings.profilesConfig:
            gm = GameMonitor(pyc)
            p = Process(target=gm.run, args=(kill_now, globalQueue, ))
            p.start()
        killer = GracefulKiller(pyc, loop)
        loop.run_until_complete(pyc.run(killer))
        loop.close()
        if p:
            p.join(timeout=1)
    except Exception as e:
        log.error(f"Error in Main: {e}")
        log.debug(f"[DEBUG] for Main: {traceback.format_exc()}")
