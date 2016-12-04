#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This package holds the code that grabs input from the device and reads it out to the custom evdev input


import logging
from select import select
import threading


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('DeviceInputWorker')


class DeviceInputWorker(threading.Thread):

    device = None
    inputDevices = None
    outputDevice = None
    killer = None
    events = []

    def __init__(self, device, killer, autoRun=True):
        self.device = device
        self.inputDevices = {dev.fd: dev for dev in self.device.device}
        self.outputDevice = self.device.outDevice
        self.killer = killer
        super(DeviceInputWorker, self).__init__()
        if autoRun:
            self.start()

    def run(self):
        try:
            while not self.killer.kill_now:
                r, w, x = select(self.inputDevices, [], [], 1)
                for fd in r:
                    for event in self.inputDevices[fd].read():
                        print event
                        self.events.append(event)
                        self.outputDevice.write_event(self.device.mapEvent(event))
                self.outputDevice.syn()
        except Exception as e:
            log.error("An Exception occurred on Device: %s\n%s\n" % (self.device.name, e))
            return None
        return None
