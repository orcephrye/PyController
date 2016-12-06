#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description: This package holds the code that grabs input from the device and reads it out to the custom evdev input


import logging
import threading
from select import select
from evdev import ecodes


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('DeviceInputWorker')


class DeviceInputWorker(threading.Thread):
    """
        This is a simple implementation of a thread. It should auto start and not die until the killer says so.
    """

    device = None
    inputDevices = None
    outputDevice = None
    killer = None

    def __init__(self, device, killer, autoRun=True):
        """
            This takes information from the Device object and puts it into its own local variables to be used by the
            'run' method later.
        :param device: Device object
        :param killer: GraceFullKiller object
        :param autoRun: bool: Default: True
        """
        log.info("Initializing Device Input Worker for device: %s" % device.name)
        self.device = device
        self.inputDevices = {dev.fd: dev for dev in self.device.device}
        self.outputDevice = self.device.outDevice
        self.killer = killer
        super(DeviceInputWorker, self).__init__()
        if autoRun:
            log.info("Auto starting Device Input Worker for: %s" % device.name)
            self.start()

    def run(self):
        """
            Overridden method of the Thread class. Runs in an new thread when you run 'self.start()'. This creates a
            while loop that will not end until the killer tells it is over or an exception happens. Its job is to listen
            for events and write them out to the custom UInput device after they have been mapped.
        :return:
        """
        try:
            while not self.killer.kill_now:
                r, w, x = select(self.inputDevices, [], [], 1)
                for fd in r:
                    for event in self.inputDevices[fd].read():
                        log.debug("The event: ( %s ) : was received and will now be mapped and written " % event)
                        if event.type == ecodes.EV_KEY:
                            self.outputDevice.write_event(self.device.mapEvent(event))
                        else:
                            self.outputDevice.write_event(event)
                self.outputDevice.syn()
        except Exception as e:
            log.error("An Exception occurred on Device: %s\n%s\n" % (self.device.name, e))
            return None
        return None
