#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.4
# Date: 12/01/2016
# Description: This is a game pad key mapping tool may originally for the Razor Nostromo to run on Linux.


import logging
import signal
import asyncio
import warnings
import traceback
import sys
from ArgumentWrapper import getArguments
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
    return kwargs.get('_default', None)


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
        signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
        for s in signals:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(self.exit_gracefully(s)))

    async def exit_gracefully(self, s):
        try:
            logging.info(f"Received exit signal {s.name}...")
            global kill_now
            kill_now.value = 0
            log.info("Changed kill value")

            tasks = [t for t in asyncio.all_tasks() if t is not
                     asyncio.current_task()]

            log.debug(f"The tasks are: {tasks}")

            log.info(f"Cancelling {len(tasks)} outstanding tasks")
            [task.cancel() for task in tasks]

            log.info(f"waiting on {len(tasks)} outstanding tasks")
            await asyncio.gather(*tasks, return_exceptions=True)

            self.loop.stop()
            log.info("Finished stopping tasks")
        except Exception as e:
            log.error(f"Error in Main: {e}")
            log.debug(f"[DEBUG] for Main: {traceback.format_exc()}")


class PyController(object):
    """
        The main class of the PyController project. This sets up all the other packages and 'gets the ball rolling'.
        It takes no arguments but uses the SettingsManager class to pull settings from the main.yaml config file.
    """

    killer = None
    arguments = None
    settings = None
    devManager = None
    devWorkers = None
    gameMonitorTask = None
    keymapper = None
    asyncLoop = None

    def __init__(self, arguments):
        self.arguments = arguments
        self.settings = Settings(self.arguments)  # This is passed to the KeyMapper and to the DeviceManager
        self.configureLogging()  # This uses the Settings manager to set the logging settings
        self.keymapper = KeyMapper(self.settings)   # This is used by the DeviceManager and is passed to each Device
        self.devManager = DeviceManager(self.settings, self.keymapper)  # This setups all the devices found in devices.d
        self.devWorkers = []    # This is where the AsyncDeviceWorker coroutines/tasks are stored

    def setup(self, loop, killer):
        log.info("Setting up PyController!")
        self.killer = killer
        self.devManager.grabDevices()

        log.info("Making Device Input Tasks")
        for device in self.devManager.devices:
            if device.isValid:
                self.devWorkers.append(loop.create_task(AsyncDeviceWorker(device)))

        if self.settings.profilesConfig:
            self.gameMonitorTask = loop.create_task(self.gameMonitor())

        return self.devWorkers

    def run(self, *args, **kwargs):
        """
            This grabs the devices from devManager and then starts all the DeviceInputWorkers. It then sits in a while
            loop waiting for a kill signal. Its job once the signal is received is to clean up by exiting the DIWs,
            releasing grabbed devices and closing any created input devices.
        :return: None
        """

        log.info("Setting up and running PyController")
        global killer
        loop = asyncio.get_event_loop()

        try:
            killer = GracefulKiller(self, loop)
            self.setup(loop, killer)
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Process interrupted")
        finally:
            log.info("Task is now complete closing and shutting down")
            self.shutdown()
            loop.close()

        log.info("Finished now exiting")
        return

    def shutdown(self):
        try:
            log.info("Disconnecting Devices")
            self.devManager.ungrabDevices()
            self.devManager.closeDevices()
            self.devManager.deleteInputs()
            log.info("Ending PyController!")
        except Exception as e:
            log.error(f"Error in Main: {e}")
            log.debug(f"[DEBUG] for Main: {traceback.format_exc()}")

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

        loglevel = 100

        if self.arguments.verbosity > 0:
            loglevel = max(10, 40 - (self.arguments.verbosity * 10))
        elif self.settings.logging:
            loglevel = getattr(logging, self.settings.loggingLevel, 40) or 40

        log.setLevel(loglevel)
        logging.getLogger('Devices').setLevel(loglevel)
        logging.getLogger('ConfigLoader').setLevel(loglevel)
        logging.getLogger('KeyMapper').setLevel(loglevel)
        logging.getLogger('GameMonitor').setLevel(loglevel)

        if self.settings.logFile:
            logging.basicConfig(filename=self.settings.logFile,
                                format='%(module)s %(funcName)s %(lineno)s %(message)s')
        else:
            logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s')


def print_list(pyc):
    print("\nBelow is a list of all accessible devices. There may appear to be duplicates.\n")
    print(pyc.devManager)
    print("\nIf the list doesn't show your device but 'lsusb' does then the app doesn't have permission access "
          "the device. You can verify by running as root. \n[NOTE: It is not recommended to run this application as "
          "root for daily use only for troubleshooting.] \nUsually adding a group to the desired user will solve this "
          "issue.\n")
    pyc.devManager.closeDevices()
    pyc.devManager.deleteInputs()
    return


def main():
    p = None
    args = getArguments()
    try:
        pyc = PyController(args)
        if args.list_devices:
            return print_list(pyc)
        if pyc.settings.profilesConfig:
            log.info("Making a Game monitor because profiles have been configured.")
            gm = GameMonitor(pyc)
            p = Process(target=gm.run, args=(kill_now, globalQueue,))
            p.start()
        pyc.run()
    except Exception as e:
        log.error(f"Error in Main: {e}")
        log.debug(f"[DEBUG] for Main: {traceback.format_exc()}")
    finally:
        if p:
            log.info("Closing profile monitor")
            p.join(timeout=1)


if __name__ == '__main__':
    main()
    sys.exit(0)
