#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description: Monitors processes on the local machine for games noted in configs found under profiles.d/*.yaml.
#   Once a game is detected it loads the keymap profile and will unload the keymap once the game is no longer running.


import logging
import psutil
import time
import traceback


# logging.basicConfig(format='%(module)s %(funcName)s %(lineno)s %(message)s', level=logging.DEBUG)
log = logging.getLogger('GameMonitor')


class GameMonitor(object):

    games = None
    settings = None
    activeGames = None
    keymap = None
    pyc = None

    def __init__(self, pyc):
        super(GameMonitor, self).__init__()
        self.settings = pyc.settings
        self.games = pyc.settings.games
        self.activeGames = set()
        self.keymap = pyc.keymapper
        for key, value in self.settings.profilesConfig.items():
            # self.keymap.addProfileKeyMap(value.get('keys'), key)
            self.keymap.add_profile_keymap(value.get('keys'), key)

    def run(self, kill_now, globalQueue):
        try:
            while bool(kill_now.value):
                procs = [proc.exe().lower() for proc in psutil.process_iter()]
                for proc in procs:
                    if [g for g in self.games if g in proc or proc in g] and proc not in self.activeGames:
                        profile = self.findProfile(proc)
                        if profile is None:
                            continue
                        self.activeGames.add(proc)
                        globalQueue.put_nowait(('makeProfileActive', profile))
                for activeGame in [games for games in self.activeGames]:
                    if activeGame not in procs:
                        profile = self.findProfile(activeGame)
                        if profile is None:
                            continue
                        self.activeGames.remove(activeGame)
                        globalQueue.put_nowait(('deactivateProfile', profile))
                time.sleep(5)
        except (KeyboardInterrupt, SystemExit):
            log.info("Game Monitor received a KeyboardInterrupt or SystemExit")
        except Exception as e:
            log.error(f'Error in the GameMonitor: {e}')
            log.debug(f'[DEBUG] for the GameMonitor: {traceback.format_exc()}')

    def findProfile(self, game):
        for profile, values in self.settings.profilesConfig.items():
            if type(values['executable']) is list:
                for exe in values['executable']:
                    if exe.lower() in game:
                        return profile
            else:
                if values['executable'].lower() in game:
                    return profile
        return None
