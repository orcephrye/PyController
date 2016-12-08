#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Version: 0.2
# Date: 12/01/2016
# Description:


import logging
import psutil
import threading
import time


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('GameMonitor')


class GameMonitor(threading.Thread):

    games = None
    settings = None
    killer = None
    activeGames = None
    keymap = None

    def __init__(self, settings, killer, keymap):
        super(GameMonitor, self).__init__()
        self.settings = settings
        self.games = settings.games
        self.killer = killer
        self.activeGames = set()
        self.keymap = keymap
        if self.games:
            self.start()

    def updateGamesList(self, autostart=False):
        self.settings.loadProfiles()
        self.games = self.settings.games
        if autostart and self.games and not self.is_alive and not self.killer.kill_now:
            self.start()

    def run(self):
        while not self.killer.kill_now:
            procs = [proc.name().lower() for proc in psutil.process_iter()]
            for proc in procs:
                if proc in self.games and proc not in self.activeGames:
                    self.activeGames.add(proc)
                    profile = self.findProfile(proc)
                    for key, value in profile.items():
                        self.keymap.updateProfileKeyMap(value['keys'], key)
            for activeGame in self.activeGames:
                if activeGame.lower() not in procs:
                    profile = self.findProfile(activeGame.lower())
                    for key in profile.keys():
                        self.keymap.removeProfile(key)
            time.sleep(1)

    def findProfile(self, game):
        for profile, values in self.settings.profileConfig.items():
            if type(values['executable']) is list:
                for exe in values['executable']:
                    if game.lower() == exe.lower():
                        return {profile: values}
            else:
                if game.lower() == values['executable'].lower():
                    return {profile: values}
        return {}
