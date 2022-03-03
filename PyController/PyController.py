#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.9
# Date: 12/01/2016
# Description: This is a game pad key mapping tool may originally for the Razor Nostromo to run on Linux. However, this
# has been tested on multiple different devices and should work for any USB device that has KEY events.


import logging
import signal
import asyncio
import warnings
import traceback
import sys
from PyController.ArgumentWrapper import getArguments, CLASSIC_KEYBOARD, CONTROLLER_BUTTONS
from multiprocessing import Process, Value, Queue
from PyController.PyDevices import DeviceManager, async_device_worker, Device
from PyController.SettingsManager import SettingsManager as Settings
from PyController.GameMonitor import GameMonitor
from PyController.KeyMap import KeyMapper


# For development debuging purposes ONLY
# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('PyControlMain')
warnings.filterwarnings("ignore", category=RuntimeWarning)


kill_now = Value('i', 1)    # Global variable for controlling the GameMonitor process
global_queue = Queue()  # Global multiprocess queue for sending signals for game monitoring


def dummy_function(*args, **kwargs):
    log.warning(f'This dummy function was called which should never happen')
    return kwargs.get('_default', None)


class GracefulKiller(object):
    """
        This class is designed to be instantiated once and then passed around to all the Device classes to be
        used as a stop gap for when a kill signal as been received. It is also used in the 'run' method of the
        GameMonitor class. It changes the 'kill_now' value to 0 to end otherwise infinite while loop and it also
        cancels and gathers all coroutines and stops the Asysnc loop.
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
            log.error(f"Error in exit_gracefully: {e}")
            log.debug(f"[DEBUG] for exit_gracefully: {traceback.format_exc()}")


class PyController(object):
    """
        The main class of the PyController project. This sets up all the other packages and 'gets the ball rolling'.
        It gets passed an ArgParse namespace that has parsed as well as the current installed directory.
    """

    killer = None
    install_dir = None
    arguments = None
    settings = None
    devManager = None
    devWorkers = None
    gameMonitorTask = None
    keymapper = None
    asyncLoop = None

    def __init__(self, arguments, install_dir=None):
        self.arguments = arguments
        self.install_dir = install_dir
        self.settings = Settings(self.arguments, install_dir=self.install_dir)  # Manages settings
        self.configure_logging()  # This uses the Settings manager to set the logging settings
        self.keymapper = KeyMapper(self.settings)  # This is used by the DeviceManager and is passed to each Device
        self.devManager = DeviceManager(self.settings, self.keymapper)  # This setups all the devices found in devices.d
        self.devWorkers = []  # This is where the AsyncDeviceWorker coroutines/tasks are stored

    def setup(self, loop, killer):
        """
            Attempts to 'grab' all EVDev devices and then adds all 'async_device_worker' coroutines to a AsysnIO loop.
        """
        log.info("Setting up PyController!")
        self.killer = killer
        self.devManager.grab_devices()

        log.info("Making Device Input Tasks")
        for device in self.devManager.devices:
            if device.isValid:
                self.devWorkers.append(loop.create_task(async_device_worker(device)))

        if self.settings.profilesConfig:
            self.gameMonitorTask = loop.create_task(self.game_monitor())

        return self.devWorkers

    def run(self, *args, **kwargs):
        """
            This first sets up a new asysncio event loop. Then it makes the GracefulKiller and runs the 'setup' method.
            It loops forever on the asysncio which will be distributed by the GracefulKiller once told to shut down.
            It calls the 'shutdown' method after execution ends.
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
        """
            A critically important step and ungrab, closes, and deletes all EV devices. If this doesn't happen or
            something goes wrong here than it is likely the program will hang and not close properly.
        """
        try:
            log.info("Disconnecting Devices")
            self.devManager.ungrab_devices()
            self.devManager.close_devices()
            self.devManager.delete_inputs()
            log.info("Ending PyController!")
        except Exception as e:
            log.error(f"Error in shutdown: {e}")
            log.debug(f"[DEBUG] for shutdown: {traceback.format_exc()}")

    async def game_monitor(self):
        """
            This runs only if there is a profile enabled in main.yaml. It listens to the 'global_queue' queue for
            events that enable or disable different game profiles.
        """
        global global_queue
        while bool(kill_now.value):
            if not global_queue.empty():
                try:
                    value = global_queue.get_nowait()
                    log.debug(f'The received value is: {value}')
                    getattr(self.keymapper, value[0], dummy_function)(value[1])
                except Exception as e:
                    log.error(f'Error in gameMonitor PyController method: {e}')
                    log.debug(f'[DEBUG] for gameMonitor PyController method: {traceback.format_exc()}')
            await asyncio.sleep(5)

    def configure_logging(self):
        """
            Sets up the logging for the box. Gets its configuration information from SettingsManager which gets its info
            from main.yaml. Flags can be sent that override logging configuration from the settings.
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

        logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s')


def print_list(pyc):
    """
        Handles the '--print-devices' flag
    """
    print("\nBelow is a list of all accessible devices. There may appear to be duplicates.\n")
    print(pyc.devManager)
    print("\nIf the list doesn't show your device but 'lsusb' does then the app doesn't have permission access "
          "the device. You can verify by running as root. \n[NOTE: It is not recommended to run this application as "
          "root for daily use only for troubleshooting.] \nUsually adding a group to the desired user will solve this "
          "issue.\n")
    pyc.devManager.close_devices()
    pyc.devManager.delete_inputs()


def print_classic_keys():
    """
        Handles the '--print-classic-keys' flag
    """
    print("\nBelow is a print out of most keys found on a classic keyboard. This is to be used as a reference to "
          "determine what to write in the yaml config file for a device.\n")
    print('\n'.join(CLASSIC_KEYBOARD))
    print("\nNOTE: Other keys such as multi media keys also exist: [KEY_VOLUMEDOWN, KEY_VOLUMEUP, KEY_NEXTSONG, "
          "KEY_PLAYPAUSE, KEY_PREVIOUSSONG]")


def print_controller_buttons():
    """
        Handles the '--print-controller-buttons' flag
    """
    print("\nBelow is a print out of all BUTTON type presses supported by EVDEV and thus PyController\n")
    print('\n'.join(CONTROLLER_BUTTONS))
    print("\nNOTE: This should be an exhaustive list however some buttons or triggers use ABS instead which is not"
          "supported by PyController so the events will simply be passed through to the OS.")


def _find_device(pyc, deviceid):
    """
        Helper private function used by 'print_capabilities' and 'print_key_presses'. Finds all devices that this
        application has permission to read/write.
    """
    if ':' not in deviceid:
        print(f'The device ID information [{deviceid}] is not formatted correctly. Needs to be XXXX:XXXX')
        return False
    vendorid = deviceid.split(':')[0]
    productid = deviceid.split(':')[1]
    device = Device(vendorid, productid, 'PrintCapabilities', type='EV_KEY')
    device.find_device(pyc.devManager.inputDevices)
    if not device.isValid:
        print(f'Could not find specified device: {deviceid}')
        return False
    return device


def print_capabilities(pyc):
    """
        Handles the '--print-capabilities' flag.
    """
    deviceid = pyc.arguments.print_capabilities

    device = _find_device(pyc, deviceid)
    if device is False:
        return

    caps = device.evdevice.capabilities(verbose=True)
    print(f"\nAttempting to print KEY capabilities of device: {device.evdevice}:\n")
    print("\n".join([item[0] if type(item[0]) is str else " / ".join(item[0]) for item in caps[("EV_KEY", 1)]]))
    print("\n")
    pyc.devManager.close_devices()
    pyc.devManager.delete_inputs()


def print_key_presses(pyc):
    """
        Handles the '--print-key-presses' flag.
    """
    deviceid = pyc.arguments.print_key_presses

    try:
        device = _find_device(pyc, deviceid)
        if device is False:
            return

        print(f'\nThis will capture key presses from the specified device: {device.evdevice}:\n'
              f'NOTE: press CTRL-C to exit...\n')

        for pevent in device.read_input():
            print(pevent)
    except KeyboardInterrupt as e:
        print("\nInterrupt detected gracefully exiting...")
    except Exception as e:
        log.error(f"Error in print_key_presses: {e}")
        log.debug(f"[DEBUG] for print_key_presses: {traceback.format_exc()}")
    finally:
        print("\n")
        pyc.devManager.close_devices()
        pyc.devManager.delete_inputs()


def main(install_dir=None):
    p = None
    args = getArguments()
    try:

        # Handle flags that do not require an instance of the PyController object first
        if args.print_classic_keys or args.print_controller_buttons:
            if args.print_classic_keys:
                print_classic_keys()
            if args.print_controller_buttons:
                print_controller_buttons()
            return
        if args.showconfigpath:
            print(Settings(args, install_dir=install_dir).show_config_path())
            return

        # Create the PyController instance at this point the devices will be registered
        pyc = PyController(args, install_dir=install_dir)
        if args.print_capabilities:
            return print_capabilities(pyc)
        if args.print_key_presses:
            return print_key_presses(pyc)
        if args.list_devices:
            return print_list(pyc)

        # Make a new forked process that strictly handles monitoring system processes for games specified by the profile
        if pyc.settings.profilesConfig:
            log.info("Making a Game monitor because profiles have been configured.")
            gm = GameMonitor(pyc)
            p = Process(target=gm.run, args=(kill_now, global_queue,))
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
