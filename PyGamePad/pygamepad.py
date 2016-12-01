#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.1
# Date: 12/01/2016
# Description: This is a game pad key mapping tool may originally for the Razor Nostromo to run on Linux.


import evdev
import signal
from evdev import InputDevice, UInput
from select import select
from threading import Lock


class GracefulKiller:

    kill_now = None
    _kill_now = None
    __LOCK__ = None

    def __init__(self):
        self.kill_now = False
        self.__LOCK__ = Lock()
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
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


class PyPad(object):

    killer = None
    inputDevices = None
    captureDevices = None
    devices = None
    ui = None
    vendorID = "1532"
    productID = "0111"

    def __init__(self):
        self.killer = GracefulKiller()
        self.captureDevices = []
        self.inputDevices = [InputDevice(fn) for fn in evdev.list_devices()]
        self.devices = self._setupDevices()
        self.ui = PyPad._setupOutputDevice(self.captureDevices)

    def _setupDevices(self):
        for dev in self.inputDevices:
            if self.vendorID in PyPad._toHex(dev.info.vendor) and self.productID in PyPad._toHex(dev.info.product):
                self.captureDevices.append(dev)

        PyPad._printCaptureDevices(self.captureDevices)

        PyPad._grabDevices(self.captureDevices)
        return {dev.fd: dev for dev in self.captureDevices}

    def run(self):
        while True:
            if self.killer.kill_now:
                PyPad._ungrabDevices(self.captureDevices)
                break
            r, w, x = select(self.devices, [], [])
            for fd in r:
                for event in self.devices[fd].read():
                    print event
                    PyPad._writeEvent(self.ui, event)

    @staticmethod
    def _printCaptureDevices(cDevices):
        for dev in cDevices:
            print dev

    @staticmethod
    def _setupOutputDevice(cDevices):
        if len(cDevices) == 2:
            return UInput.from_device(cDevices[0], cDevices[1], name='pynostromo')
        elif len(cDevices) == 1:
            return UInput.from_device(cDevices[0], name='pynostromo')
        else:
            raise Exception('Did not detect the correct number of devices')

    @staticmethod
    def _toHex(hexString, standardLength=4):
        return hex(hexString)[2:].rjust(standardLength, '0')

    @staticmethod
    def _grabDevices(cDevices):
        for dev in cDevices:
            dev.grab()

    @staticmethod
    def _ungrabDevices(cDevices):
        for dev in cDevices:
            dev.ungrab()

    @staticmethod
    def _writeEvent(ui, event):
        ui.write_event(event)
        ui.syn()


if __name__ == '__main__':
    PyPad().run()