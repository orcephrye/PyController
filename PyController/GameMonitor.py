#!/usr/bin/env python
# -*- coding=utf-8 -*-

# Author: Ryan Henrichson
# Description: Monitors processes on the local machine for games noted in configs found under profiles.d/*.yaml.
#   Once a game is detected it loads the keymap profile and will unload the keymap once the game is no longer running.


import logging
import psutil
import time
import traceback


log = logging.getLogger('GameMonitor')


class GameMonitor(object):
    """
        This class object is meant to be instantiated only once and ran inside a new forked process using
        multiprocess. It is simply designed to monitor processes on the machine and load and unload custom key mappings
        when a specified game runs. It uses config files located under 'profiles.d' that are enabled in main.yaml.
    """

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
            self.keymap.add_profile_keymap(value.get('default-keys'), key)
            for dev in value.get('devices', []):
                self.keymap.add_profile_keymap(dev.get('keys'), key, deviceName=dev.get('name', ''))

    def run(self, kill_now, globalQueue):
        def __psHelper(process):
            try:
                return process.exe().lower()
            except psutil.NoSuchProcess:
                return ''
            except psutil.AccessDenied:
                try:
                    process.name().lower()
                except Exception:
                    return ''
            except Exception:
                return ''

        try:
            while bool(kill_now.value):
                procs = list(filter(None, [__psHelper(proc) for proc in psutil.process_iter()]))
                for proc in procs:
                    if proc not in self.activeGames and [g for g in self.games if g in proc or proc in g]:
                        profile = self.find_profile(proc)
                        if profile is None:
                            continue
                        self.activeGames.add(proc)
                        globalQueue.put_nowait(('makeProfileActive', profile))
                for activeGame in [games for games in self.activeGames]:
                    if activeGame not in procs:
                        profile = self.find_profile(activeGame)
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

    def find_profile(self, game):
        for profile, values in self.settings.profilesConfig.items():
            if isinstance(values['executable'], list):
                for exe in values['executable']:
                    if exe.lower() in game:
                        return profile
            else:
                if values['executable'].lower() in game:
                    return profile
        return None
